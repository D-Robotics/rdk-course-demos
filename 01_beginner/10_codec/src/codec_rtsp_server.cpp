// Copyright (c) 2026 D-Robotics.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <gst/app/gstappsrc.h>
#include <gst/gst.h>
#include <gst/rtsp-server/rtsp-server.h>

#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#include "codec_common.hpp"
#include "sp_sys.h"
#include "sp_vio.h"

namespace {

struct Config {
  int width = 1920;
  int height = 1080;
  int sensor_width = 0;
  int sensor_height = 0;
  int fps = 30;
  int bitrate_kbps = 8000;
  int duration_seconds = 0;
  int pipe_id = 0;
  int camera_index = -1;
  int port = 8554;
  std::size_t stream_buffer_bytes = 4U * 1024U * 1024U;
  std::string mount = "/live";
  std::string output_path;
  lesson10::CodecSpec codec;
};

void print_usage(const char *program) {
  std::cout
      << "Usage: " << program << " [options]\n\n"
      << "Camera -> BSP hardware encoder -> RTP/RTSP server\n\n"
      << "Options:\n"
      << "  --width N           encoded width (default: 1920)\n"
      << "  --height N          encoded height (default: 1080)\n"
      << "  --sensor-width N    sensor RAW width (default: --width)\n"
      << "  --sensor-height N   sensor RAW height (default: --height)\n"
      << "  --fps N             sensor and RTP frame rate (default: 30)\n"
      << "  --codec h264|h265   codec type (default: h264)\n"
      << "  --bitrate N         encoder bitrate in kbit/s (default: 8000)\n"
      << "  --port N            RTSP listen port (default: 8554)\n"
      << "  --mount PATH        RTSP mount path (default: /live)\n"
      << "  --duration N        stop after N seconds; 0 waits for Ctrl-C\n"
      << "  --camera-index N    sensor index; -1 auto-detects (default: -1)\n"
      << "  --pipe-id N         camera VIO pipeline id (default: 0)\n"
      << "  --buffer-mb N       encoded buffer size in MiB (default: 4)\n"
      << "  --output PATH       also save the Annex-B stream\n"
      << "  --help              show this message\n";
}

Config parse_arguments(int argc, char **argv) {
  Config config;
  auto value_after = [&](int &index, const std::string &option) -> std::string {
    if (index + 1 >= argc) {
      throw std::runtime_error(option + " requires a value");
    }
    return argv[++index];
  };

  for (int i = 1; i < argc; ++i) {
    const std::string option = argv[i];
    if (option == "--help") {
      print_usage(argv[0]);
      std::exit(EXIT_SUCCESS);
    } else if (option == "--width") {
      config.width = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--height") {
      config.height = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--sensor-width") {
      config.sensor_width = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--sensor-height") {
      config.sensor_height = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--fps") {
      config.fps = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--bitrate") {
      config.bitrate_kbps =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--port") {
      config.port = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--mount") {
      config.mount = value_after(i, option);
    } else if (option == "--duration") {
      config.duration_seconds =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--camera-index") {
      config.camera_index =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--pipe-id") {
      config.pipe_id = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--buffer-mb") {
      const int megabytes =
          lesson10::parse_int(option, value_after(i, option));
      if (megabytes < 0) {
        throw std::runtime_error("--buffer-mb must not be negative");
      }
      config.stream_buffer_bytes =
          static_cast<std::size_t>(megabytes) * 1024U * 1024U;
    } else if (option == "--output") {
      config.output_path = value_after(i, option);
    } else if (option == "--codec") {
      config.codec = lesson10::codec_spec_from_name(value_after(i, option));
    } else {
      throw std::runtime_error("unknown option: " + option);
    }
  }

  if (config.sensor_width == 0) {
    config.sensor_width = config.width;
  }
  if (config.sensor_height == 0) {
    config.sensor_height = config.height;
  }
  if (config.width <= 0 || config.height <= 0 || config.sensor_width <= 0 ||
      config.sensor_height <= 0) {
    throw std::runtime_error("camera and stream dimensions must be positive");
  }
  if ((config.width % 16) != 0 || (config.height & 1) != 0) {
    throw std::runtime_error(
        "encoded width must be 16-aligned and height must be even");
  }
  if (config.fps <= 0 || config.fps > 240) {
    throw std::runtime_error("--fps must be in [1, 240]");
  }
  if (config.bitrate_kbps <= 0) {
    throw std::runtime_error("--bitrate must be positive");
  }
  if (config.port <= 0 || config.port > 65535) {
    throw std::runtime_error("--port must be in [1, 65535]");
  }
  if (config.mount.empty() || config.mount.front() != '/' ||
      config.mount.find(' ') != std::string::npos) {
    throw std::runtime_error("--mount must start with '/' and contain no spaces");
  }
  if (config.duration_seconds < 0) {
    throw std::runtime_error("--duration must be zero or positive");
  }
  if (config.pipe_id < 0) {
    throw std::runtime_error("--pipe-id must not be negative");
  }
  const std::size_t min_buffer = 2U * 1024U * 1024U;
  const std::size_t max_buffer = 32U * 1024U * 1024U;
  if (config.stream_buffer_bytes < min_buffer ||
      config.stream_buffer_bytes > max_buffer) {
    throw std::runtime_error("--buffer-mb must be in [2, 32]");
  }
  return config;
}

class AppSourceSlot {
 public:
  ~AppSourceSlot() { clear(); }

  void replace(GstElement *source) {
    auto *replacement = GST_ELEMENT(gst_object_ref(source));
    GstElement *previous = nullptr;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      previous = source_;
      source_ = replacement;
    }
    if (previous != nullptr) {
      gst_object_unref(previous);
    }
  }

  GstElement *acquire() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return source_ == nullptr ? nullptr
                              : GST_ELEMENT(gst_object_ref(source_));
  }

  void clear_if(GstElement *source) {
    GstElement *previous = nullptr;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      if (source_ == source) {
        previous = source_;
        source_ = nullptr;
      }
    }
    if (previous != nullptr) {
      gst_object_unref(previous);
    }
  }

  void clear() {
    GstElement *previous = nullptr;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      previous = source_;
      source_ = nullptr;
    }
    if (previous != nullptr) {
      gst_object_unref(previous);
    }
  }

  bool active() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return source_ != nullptr;
  }

 private:
  mutable std::mutex mutex_;
  GstElement *source_ = nullptr;
};

struct Metrics {
  std::atomic<std::uint64_t> encoded_chunks{0};
  std::atomic<std::uint64_t> encoded_bytes{0};
  std::atomic<std::uint64_t> published_chunks{0};
  std::atomic<std::uint64_t> no_client_chunks{0};
  std::atomic<std::uint64_t> push_failures{0};
  lesson10::NalMetrics nal;
};

class RtspEncoderServer {
 public:
  explicit RtspEncoderServer(Config config) : config_(std::move(config)) {}
  ~RtspEncoderServer() { cleanup(); }

  bool initialize() {
    const lesson10::PlatformProfile profile = lesson10::detect_platform();
    std::cout << "[platform] model=" << profile.model << '\n';

    if (!config_.output_path.empty()) {
      output_.open(config_.output_path, std::ios::binary | std::ios::trunc);
      if (!output_) {
        return fail("cannot open output file: " + config_.output_path);
      }
    }

    camera_ = sp_init_vio_module();
    encoder_ = sp_init_encoder_module();
    if (camera_ == nullptr || encoder_ == nullptr) {
      return fail("failed to create Camera/Encoder BSP objects");
    }

    sp_sensors_parameters sensor{};
    sensor.raw_width = config_.sensor_width;
    sensor.raw_height = config_.sensor_height;
    sensor.fps = config_.fps;
    stream_width_ = config_.width;
    stream_height_ = config_.height;
    int ret = sp_open_camera_v2(camera_, config_.pipe_id, config_.camera_index,
                                1, &sensor, &stream_width_, &stream_height_);
    if (ret != 0) {
      return fail("sp_open_camera_v2 failed, ret=" + std::to_string(ret));
    }
    camera_open_ = true;

    ret = sp_start_encode(encoder_, 0, config_.codec.sp_type, stream_width_,
                          stream_height_, config_.bitrate_kbps);
    if (ret != 0) {
      return fail("sp_start_encode failed, ret=" + std::to_string(ret));
    }
    encoder_started_ = true;

    ret = sp_module_bind(camera_, SP_MTYPE_VIO, encoder_, SP_MTYPE_ENCODER);
    if (ret != 0) {
      return fail("sp_module_bind(camera, encoder) failed, ret=" +
                  std::to_string(ret));
    }
    camera_encoder_bound_ = true;

    if (!initialize_rtsp()) {
      return false;
    }

    std::cout << "[camera] sensor=" << config_.sensor_width << 'x'
              << config_.sensor_height << " output=" << stream_width_ << 'x'
              << stream_height_ << " fps=" << config_.fps << '\n';
    std::cout << "[codec] " << config_.codec.name
              << " bitrate=" << config_.bitrate_kbps << " kbit/s\n";
    std::cout << "[rtsp] ready: rtsp://<board-ip>:" << config_.port
              << config_.mount << '\n';
    std::cout << "[rtsp] same-board client: rtsp://127.0.0.1:"
              << config_.port << config_.mount << '\n';
    return true;
  }

  bool run() {
    started_at_ = std::chrono::steady_clock::now();
    last_report_at_ = started_at_;
    producer_thread_ = std::thread(&RtspEncoderServer::produce, this);
    tick_source_id_ = g_timeout_add(100, &RtspEncoderServer::tick_callback, this);
    g_main_loop_run(main_loop_);

    request_stop();
    join_producer();
    report_metrics(std::chrono::steady_clock::now(), true);

    if (failed_.load()) {
      std::lock_guard<std::mutex> lock(error_mutex_);
      std::cerr << "[result] FAIL: " << first_error_ << '\n';
      return false;
    }
    if (metrics_.encoded_chunks.load() == 0) {
      std::cerr << "[result] FAIL: encoder produced no stream chunks\n";
      return false;
    }
    if (metrics_.nal.sps.load() == 0 || metrics_.nal.pps.load() == 0) {
      std::cerr << "[result] FAIL: encoded stream contained no SPS/PPS\n";
      return false;
    }
    std::cout << "[result] PASS: camera, BSP hardware encoder and RTSP server "
                 "ran successfully\n";
    return true;
  }

 private:
  struct MediaContext {
    AppSourceSlot *slot = nullptr;
    GstElement *source = nullptr;
  };

  static void media_configure_callback(GstRTSPMediaFactory *,
                                       GstRTSPMedia *media,
                                       gpointer user_data) {
    static_cast<RtspEncoderServer *>(user_data)->configure_media(media);
  }

  static void media_unprepared_callback(GstRTSPMedia *, gpointer user_data) {
    auto *context = static_cast<MediaContext *>(user_data);
    context->slot->clear_if(context->source);
  }

  static void destroy_media_context(gpointer data, GClosure *) {
    auto *context = static_cast<MediaContext *>(data);
    if (context->source != nullptr) {
      gst_object_unref(context->source);
    }
    delete context;
  }

  static gboolean tick_callback(gpointer user_data) {
    return static_cast<RtspEncoderServer *>(user_data)->tick();
  }

  bool initialize_rtsp() {
    rtsp_server_ = gst_rtsp_server_new();
    if (rtsp_server_ == nullptr) {
      return fail("gst_rtsp_server_new failed");
    }
    const std::string service = std::to_string(config_.port);
    gst_rtsp_server_set_address(rtsp_server_, "0.0.0.0");
    gst_rtsp_server_set_service(rtsp_server_, service.c_str());

    GstRTSPMountPoints *mounts = gst_rtsp_server_get_mount_points(rtsp_server_);
    GstRTSPMediaFactory *factory = gst_rtsp_media_factory_new();
    if (mounts == nullptr || factory == nullptr) {
      if (mounts != nullptr) {
        gst_object_unref(mounts);
      }
      if (factory != nullptr) {
        g_object_unref(factory);
      }
      return fail("failed to create RTSP mount/factory");
    }

    std::ostringstream launch;
    launch << "( appsrc name=source is-live=true format=time "
              "do-timestamp=true block=false caps=\""
           << config_.codec.media_type
           << ",stream-format=(string)byte-stream,alignment=(string)au,"
              "width=(int)"
           << stream_width_ << ",height=(int)" << stream_height_
           << ",framerate=(fraction)" << config_.fps << "/1\" ! "
           << config_.codec.parser << " config-interval=-1 ! "
           << config_.codec.payloader
           << " name=pay0 pt=96 config-interval=1 )";
    gst_rtsp_media_factory_set_launch(factory, launch.str().c_str());
    gst_rtsp_media_factory_set_shared(factory, TRUE);
    gst_rtsp_media_factory_set_eos_shutdown(factory, TRUE);
    g_signal_connect(factory, "media-configure",
                     G_CALLBACK(&RtspEncoderServer::media_configure_callback),
                     this);
    gst_rtsp_mount_points_add_factory(mounts, config_.mount.c_str(), factory);
    gst_object_unref(mounts);

    main_loop_ = g_main_loop_new(nullptr, FALSE);
    if (main_loop_ == nullptr) {
      return fail("g_main_loop_new failed");
    }
    attach_source_id_ = gst_rtsp_server_attach(rtsp_server_, nullptr);
    if (attach_source_id_ == 0) {
      return fail("failed to bind RTSP listen port " +
                  std::to_string(config_.port));
    }
    return true;
  }

  void configure_media(GstRTSPMedia *media) {
    GstElement *element = gst_rtsp_media_get_element(media);
    if (element == nullptr || !GST_IS_BIN(element)) {
      if (element != nullptr) {
        gst_object_unref(element);
      }
      set_failure("RTSP factory did not create a media bin");
      return;
    }
    GstElement *source =
        gst_bin_get_by_name_recurse_up(GST_BIN(element), "source");
    gst_object_unref(element);
    if (source == nullptr || !GST_IS_APP_SRC(source)) {
      if (source != nullptr) {
        gst_object_unref(source);
      }
      set_failure("RTSP media contains no appsrc named 'source'");
      return;
    }

    g_object_set(source, "is-live", TRUE, "format", GST_FORMAT_TIME,
                 "do-timestamp", TRUE, "block", FALSE, nullptr);
    source_slot_.replace(source);

    auto *context = new MediaContext;
    context->slot = &source_slot_;
    context->source = GST_ELEMENT(gst_object_ref(source));
    g_signal_connect_data(
        media, "unprepared",
        G_CALLBACK(&RtspEncoderServer::media_unprepared_callback), context,
        &RtspEncoderServer::destroy_media_context,
        static_cast<GConnectFlags>(0));
    gst_object_unref(source);
    std::cout << "[rtsp] client media configured\n";
  }

  gboolean tick() {
    const auto now = std::chrono::steady_clock::now();
    if (lesson10::signal_stop_requested()) {
      std::cout << "[control] signal received, stopping\n";
      request_stop();
    }
    if (config_.duration_seconds > 0 &&
        now - started_at_ >= std::chrono::seconds(config_.duration_seconds)) {
      std::cout << "[control] duration reached, stopping\n";
      request_stop();
    }
    if (now - last_report_at_ >= std::chrono::seconds(1)) {
      report_metrics(now, false);
    }
    if (stop_requested_.load() || failed_.load()) {
      tick_source_id_ = 0;
      g_main_loop_quit(main_loop_);
      return G_SOURCE_REMOVE;
    }
    return G_SOURCE_CONTINUE;
  }

  void produce() {
    std::vector<char> stream(config_.stream_buffer_bytes);
    while (!stop_requested_.load()) {
      const int encoded_size = sp_encoder_get_stream(encoder_, stream.data());
      if (encoded_size <= 0) {
        if (!stop_requested_.load()) {
          set_failure("sp_encoder_get_stream failed, ret=" +
                      std::to_string(encoded_size));
        }
        break;
      }
      const std::size_t size = static_cast<std::size_t>(encoded_size);
      if (size > stream.size()) {
        set_failure("encoded chunk exceeded --buffer-mb capacity");
        break;
      }

      if (output_.is_open()) {
        output_.write(stream.data(), encoded_size);
        if (!output_) {
          set_failure("failed while writing encoded output file");
          break;
        }
      }

      lesson10::inspect_annex_b(stream.data(), size, config_.codec.sp_type,
                                metrics_.nal);
      ++metrics_.encoded_chunks;
      metrics_.encoded_bytes.fetch_add(size);

      GstElement *source = source_slot_.acquire();
      if (source == nullptr) {
        ++metrics_.no_client_chunks;
        continue;
      }

      GstBuffer *buffer = gst_buffer_new_allocate(nullptr, size, nullptr);
      if (buffer == nullptr) {
        gst_object_unref(source);
        set_failure("gst_buffer_new_allocate failed");
        break;
      }
      gst_buffer_fill(buffer, 0, stream.data(), size);
      GST_BUFFER_DURATION(buffer) =
          gst_util_uint64_scale_int(GST_SECOND, 1, config_.fps);
      const GstFlowReturn flow =
          gst_app_src_push_buffer(GST_APP_SRC(source), buffer);
      gst_object_unref(source);
      if (flow == GST_FLOW_OK) {
        ++metrics_.published_chunks;
      } else {
        ++metrics_.push_failures;
      }
    }
    if (output_.is_open()) {
      output_.flush();
    }
  }

  void request_stop() { stop_requested_.store(true); }

  void set_failure(const std::string &message) {
    bool expected = false;
    if (failed_.compare_exchange_strong(expected, true)) {
      std::lock_guard<std::mutex> lock(error_mutex_);
      first_error_ = message;
    }
    request_stop();
  }

  bool fail(const std::string &message) {
    std::cerr << "[error] " << message << '\n';
    return false;
  }

  void join_producer() {
    if (producer_thread_.joinable()) {
      producer_thread_.join();
    }
  }

  void report_metrics(std::chrono::steady_clock::time_point now, bool final) {
    const std::uint64_t chunks = metrics_.encoded_chunks.load();
    const std::uint64_t bytes = metrics_.encoded_bytes.load();
    const double seconds =
        std::chrono::duration<double>(now - last_report_at_).count();
    const double chunk_rate =
        seconds > 0.0
            ? static_cast<double>(chunks - last_chunks_) / seconds
            : 0.0;
    const double bitrate =
        seconds > 0.0
            ? static_cast<double>(bytes - last_bytes_) * 8.0 / seconds /
                  1000000.0
            : 0.0;

    std::cout << (final ? "[summary]" : "[metrics]")
              << " encoded=" << chunks << " chunks"
              << " rate=" << std::fixed << std::setprecision(1) << chunk_rate
              << " chunk/s bitrate=" << std::setprecision(2) << bitrate
              << " Mbit/s published=" << metrics_.published_chunks.load()
              << " no-client=" << metrics_.no_client_chunks.load()
              << " push-fail=" << metrics_.push_failures.load()
              << " rtsp-source=" << (source_slot_.active() ? "active" : "idle")
              << " NAL(vps/sps/pps/idr)=" << metrics_.nal.vps.load() << '/'
              << metrics_.nal.sps.load() << '/' << metrics_.nal.pps.load() << '/'
              << metrics_.nal.idr.load() << '\n';
    last_report_at_ = now;
    last_chunks_ = chunks;
    last_bytes_ = bytes;
  }

  void cleanup() {
    request_stop();
    join_producer();

    GstElement *source = source_slot_.acquire();
    if (source != nullptr) {
      gst_app_src_end_of_stream(GST_APP_SRC(source));
      gst_object_unref(source);
    }
    source_slot_.clear();

    if (tick_source_id_ != 0) {
      g_source_remove(tick_source_id_);
      tick_source_id_ = 0;
    }
    if (attach_source_id_ != 0) {
      g_source_remove(attach_source_id_);
      attach_source_id_ = 0;
    }
    if (main_loop_ != nullptr) {
      g_main_loop_unref(main_loop_);
      main_loop_ = nullptr;
    }
    if (rtsp_server_ != nullptr) {
      g_object_unref(rtsp_server_);
      rtsp_server_ = nullptr;
    }

    if (camera_encoder_bound_) {
      sp_module_unbind(camera_, SP_MTYPE_VIO, encoder_, SP_MTYPE_ENCODER);
      camera_encoder_bound_ = false;
    }
    if (encoder_started_) {
      sp_stop_encode(encoder_);
      encoder_started_ = false;
    }
    if (camera_open_) {
      sp_vio_close(camera_);
      camera_open_ = false;
    }
    if (encoder_ != nullptr) {
      sp_release_encoder_module(encoder_);
      encoder_ = nullptr;
    }
    if (camera_ != nullptr) {
      sp_release_vio_module(camera_);
      camera_ = nullptr;
    }
    if (output_.is_open()) {
      output_.close();
    }
  }

  Config config_;
  Metrics metrics_;
  AppSourceSlot source_slot_;
  std::ofstream output_;

  void *camera_ = nullptr;
  void *encoder_ = nullptr;
  int stream_width_ = 0;
  int stream_height_ = 0;
  bool camera_open_ = false;
  bool encoder_started_ = false;
  bool camera_encoder_bound_ = false;

  GstRTSPServer *rtsp_server_ = nullptr;
  GMainLoop *main_loop_ = nullptr;
  guint attach_source_id_ = 0;
  guint tick_source_id_ = 0;

  std::atomic<bool> stop_requested_{false};
  std::atomic<bool> failed_{false};
  std::mutex error_mutex_;
  std::string first_error_;
  std::thread producer_thread_;
  std::chrono::steady_clock::time_point started_at_{};
  std::chrono::steady_clock::time_point last_report_at_{};
  std::uint64_t last_chunks_ = 0;
  std::uint64_t last_bytes_ = 0;
};

}  // namespace

int main(int argc, char **argv) {
  try {
    gst_init(&argc, &argv);
    Config config = parse_arguments(argc, argv);
    lesson10::install_signal_handlers();

    bool ok = false;
    {
      RtspEncoderServer server(std::move(config));
      ok = server.initialize() && server.run();
    }
    gst_deinit();
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
  } catch (const std::exception &error) {
    std::cerr << "[error] " << error.what() << '\n';
    return EXIT_FAILURE;
  }
}
