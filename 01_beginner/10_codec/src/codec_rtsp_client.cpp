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

#include <gst/app/gstappsink.h>
#include <gst/gst.h>
#include <gst/rtsp/gstrtsptransport.h>

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

namespace {

struct Config {
  std::string url = "rtsp://127.0.0.1:8554/live";
  int width = 1920;
  int height = 1080;
  int duration_seconds = 0;
  int latency_ms = 100;
  int vps_pipe_id = 1;
  int display_channel = -1;
  int display_width = 0;
  int display_height = 0;
  bool headless = false;
  bool use_tcp = true;
  std::string snapshot_path;
  lesson10::CodecSpec codec;
};

void print_usage(const char *program) {
  std::cout
      << "Usage: " << program << " [options]\n\n"
      << "RTSP/RTP depay -> BSP hardware decoder -> Display or headless sink\n\n"
      << "Options:\n"
      << "  --url URL             RTSP URL (default: rtsp://127.0.0.1:8554/live)\n"
      << "  --width N             decoded width (default: 1920)\n"
      << "  --height N            decoded height (default: 1080)\n"
      << "  --codec h264|h265     codec type (default: h264)\n"
      << "  --transport tcp|udp   RTP transport (default: tcp)\n"
      << "  --latency N           RTSP jitter-buffer latency in ms (default: 100)\n"
      << "  --duration N          stop after N seconds; 0 waits for Ctrl-C\n"
      << "  --headless            drain decoded NV12 without Display\n"
      << "  --snapshot PATH       save first decoded NV12 frame (headless only)\n"
      << "  --vps-pipe-id N       display VPS pipeline id (default: 1)\n"
      << "  --display-channel N   override platform display channel\n"
      << "  --display-width N     override detected display width\n"
      << "  --display-height N    override detected display height\n"
      << "  --help                show this message\n";
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
    } else if (option == "--url") {
      config.url = value_after(i, option);
    } else if (option == "--width") {
      config.width = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--height") {
      config.height = lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--codec") {
      config.codec = lesson10::codec_spec_from_name(value_after(i, option));
    } else if (option == "--transport") {
      const std::string transport = value_after(i, option);
      if (transport == "tcp") {
        config.use_tcp = true;
      } else if (transport == "udp") {
        config.use_tcp = false;
      } else {
        throw std::runtime_error("--transport must be tcp or udp");
      }
    } else if (option == "--latency") {
      config.latency_ms =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--duration") {
      config.duration_seconds =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--headless") {
      config.headless = true;
    } else if (option == "--snapshot") {
      config.snapshot_path = value_after(i, option);
    } else if (option == "--vps-pipe-id") {
      config.vps_pipe_id =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--display-channel") {
      config.display_channel =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--display-width") {
      config.display_width =
          lesson10::parse_int(option, value_after(i, option));
    } else if (option == "--display-height") {
      config.display_height =
          lesson10::parse_int(option, value_after(i, option));
    } else {
      throw std::runtime_error("unknown option: " + option);
    }
  }

  if (config.url.rfind("rtsp://", 0) != 0 &&
      config.url.rfind("rtsps://", 0) != 0) {
    throw std::runtime_error("--url must start with rtsp:// or rtsps://");
  }
  if (config.width <= 0 || config.height <= 0 ||
      (config.width % 16) != 0 || (config.height & 1) != 0) {
    throw std::runtime_error(
        "decoded width must be positive and 16-aligned; height must be even");
  }
  if (config.duration_seconds < 0) {
    throw std::runtime_error("--duration must be zero or positive");
  }
  if (config.latency_ms < 0 || config.latency_ms > 5000) {
    throw std::runtime_error("--latency must be in [0, 5000]");
  }
  if (config.vps_pipe_id < 0) {
    throw std::runtime_error("--vps-pipe-id must not be negative");
  }
  const bool one_display_dimension =
      (config.display_width > 0) != (config.display_height > 0);
  if (one_display_dimension) {
    throw std::runtime_error(
        "--display-width and --display-height must be specified together");
  }
  if (!config.snapshot_path.empty() && !config.headless) {
    throw std::runtime_error("--snapshot requires --headless");
  }
  return config;
}

struct Metrics {
  std::atomic<std::uint64_t> received_buffers{0};
  std::atomic<std::uint64_t> received_bytes{0};
  std::atomic<std::uint64_t> decoder_submissions{0};
  std::atomic<std::uint64_t> decoded_frames{0};
  lesson10::NalMetrics nal;
};

class RtspDecoderClient {
 public:
  explicit RtspDecoderClient(Config config) : config_(std::move(config)) {}
  ~RtspDecoderClient() { cleanup(); }

  bool initialize() {
    const lesson10::PlatformProfile profile = lesson10::detect_platform();
    std::cout << "[platform] model=" << profile.model << '\n';

    decoder_ = sp_init_decoder_module();
    if (decoder_ == nullptr) {
      return fail("sp_init_decoder_module failed");
    }
    const int ret = sp_start_decode(decoder_, "", 0, config_.codec.sp_type,
                                    config_.width, config_.height);
    if (ret != 0) {
      return fail("sp_start_decode failed, ret=" + std::to_string(ret));
    }
    decoder_started_ = true;

    if (!config_.headless) {
      lesson10::DisplayConfig display_config;
      display_config.vps_pipe_id = config_.vps_pipe_id;
      display_config.display_channel = config_.display_channel;
      display_config.display_width = config_.display_width;
      display_config.display_height = config_.display_height;
      if (!display_path_.initialize(decoder_, config_.width, config_.height,
                                    display_config)) {
        return fail(display_path_.error());
      }
    }

    if (!initialize_gstreamer()) {
      return false;
    }

    std::cout << "[codec] BSP hardware decoder=" << config_.codec.name
              << " size=" << config_.width << 'x' << config_.height << '\n';
    std::cout << "[rtsp] transport=" << (config_.use_tcp ? "tcp" : "udp")
              << " latency=" << config_.latency_ms << " ms\n";
    if (config_.headless) {
      std::cout << "[sink] headless NV12 drain";
      if (!config_.snapshot_path.empty()) {
        std::cout << " snapshot=" << config_.snapshot_path;
      }
      std::cout << '\n';
    } else {
      std::cout << "[sink] Decoder -> VPS -> Display " << display_path_.width()
                << 'x' << display_path_.height()
                << " channel=" << display_path_.channel() << '\n';
    }
    return true;
  }

  bool run() {
    const GstStateChangeReturn state =
        gst_element_set_state(pipeline_, GST_STATE_PLAYING);
    if (state == GST_STATE_CHANGE_FAILURE) {
      return fail("failed to set RTSP pipeline to PLAYING");
    }
    pipeline_started_ = true;
    started_at_ = std::chrono::steady_clock::now();
    last_report_at_ = started_at_;

    if (config_.headless) {
      drain_thread_ = std::thread(&RtspDecoderClient::drain_decoder, this);
    }
    feeder_thread_ = std::thread(&RtspDecoderClient::feed_decoder, this);

    while (!stop_requested_.load() && !failed_.load()) {
      const auto now = std::chrono::steady_clock::now();
      if (lesson10::signal_stop_requested()) {
        std::cout << "[control] signal received, stopping\n";
        request_stop();
        break;
      }
      if (config_.duration_seconds > 0 &&
          now - started_at_ >= std::chrono::seconds(config_.duration_seconds)) {
        std::cout << "[control] duration reached, stopping\n";
        request_stop();
        break;
      }
      if (now - last_report_at_ >= std::chrono::seconds(1)) {
        report_metrics(now, false);
      }

      GstMessage *message = gst_bus_timed_pop_filtered(
          bus_, 100 * GST_MSECOND,
          static_cast<GstMessageType>(GST_MESSAGE_ERROR | GST_MESSAGE_EOS));
      if (message == nullptr) {
        continue;
      }
      if (GST_MESSAGE_TYPE(message) == GST_MESSAGE_ERROR) {
        GError *error = nullptr;
        gchar *debug = nullptr;
        gst_message_parse_error(message, &error, &debug);
        std::string text = error == nullptr ? "unknown GStreamer error"
                                            : error->message;
        if (debug != nullptr) {
          text += " (" + std::string(debug) + ")";
        }
        if (error != nullptr) {
          g_error_free(error);
        }
        g_free(debug);
        gst_message_unref(message);
        set_failure("RTSP pipeline: " + text);
        break;
      }
      if (GST_MESSAGE_TYPE(message) == GST_MESSAGE_EOS) {
        std::cout << "[rtsp] end of stream\n";
        request_stop();
      }
      gst_message_unref(message);
    }

    stop_pipeline_and_threads();
    report_metrics(std::chrono::steady_clock::now(), true);

    if (failed_.load()) {
      std::lock_guard<std::mutex> lock(error_mutex_);
      std::cerr << "[result] FAIL: " << first_error_ << '\n';
      return false;
    }
    if (!rtp_pad_linked_.load()) {
      std::cerr << "[result] FAIL: RTSP source exposed no matching video RTP pad\n";
      return false;
    }
    if (metrics_.decoder_submissions.load() == 0) {
      std::cerr << "[result] FAIL: BSP decoder received no elementary stream\n";
      return false;
    }
    if (config_.headless && metrics_.decoded_frames.load() == 0) {
      std::cerr << "[result] FAIL: BSP decoder produced no NV12 frames\n";
      return false;
    }
    std::cout << "[result] PASS: RTSP/RTP depay and BSP hardware decode ran "
              << (config_.headless ? "in headless mode\n"
                                   : "with Display output\n");
    return true;
  }

 private:
  static void pad_added_callback(GstElement *, GstPad *pad,
                                 gpointer user_data) {
    static_cast<RtspDecoderClient *>(user_data)->link_rtp_pad(pad);
  }

  GstElement *make_element(const char *factory, const char *name) {
    GstElement *element = gst_element_factory_make(factory, name);
    if (element == nullptr) {
      set_failure(std::string("missing GStreamer element: ") + factory);
    }
    return element;
  }

  bool initialize_gstreamer() {
    pipeline_ = gst_pipeline_new("lesson10-rtsp-client");
    source_ = make_element("rtspsrc", "source");
    depayloader_ = make_element(config_.codec.depayloader.c_str(), "depay");
    parser_ = make_element(config_.codec.parser.c_str(), "parse");
    caps_filter_ = make_element("capsfilter", "byte-stream-caps");
    appsink_element_ = make_element("appsink", "encoded-sink");
    if (pipeline_ == nullptr || source_ == nullptr || depayloader_ == nullptr ||
        parser_ == nullptr || caps_filter_ == nullptr ||
        appsink_element_ == nullptr) {
      return fail("failed to construct RTSP client pipeline");
    }

    const GstRTSPLowerTrans protocols = config_.use_tcp
                                           ? GST_RTSP_LOWER_TRANS_TCP
                                           : GST_RTSP_LOWER_TRANS_UDP;
    g_object_set(source_, "location", config_.url.c_str(), "latency",
                 config_.latency_ms, "protocols", protocols,
                 "drop-on-latency", TRUE, nullptr);

    GstCaps *caps = gst_caps_new_simple(
        config_.codec.media_type.c_str(), "stream-format", G_TYPE_STRING,
        "byte-stream", "alignment", G_TYPE_STRING, "au", nullptr);
    g_object_set(caps_filter_, "caps", caps, nullptr);
    gst_caps_unref(caps);

    g_object_set(appsink_element_, "emit-signals", FALSE, "sync", FALSE,
                 "max-buffers", 16U, "drop", FALSE, nullptr);
    appsink_ = GST_APP_SINK(appsink_element_);

    gst_bin_add_many(GST_BIN(pipeline_), source_, depayloader_, parser_,
                     caps_filter_, appsink_element_, nullptr);
    if (!gst_element_link_many(depayloader_, parser_, caps_filter_,
                               appsink_element_, nullptr)) {
      return fail("failed to link RTP depay/parser/appsink elements");
    }
    g_signal_connect(source_, "pad-added",
                     G_CALLBACK(&RtspDecoderClient::pad_added_callback), this);
    bus_ = gst_element_get_bus(pipeline_);
    if (bus_ == nullptr) {
      return fail("gst_element_get_bus failed");
    }
    return true;
  }

  void link_rtp_pad(GstPad *pad) {
    GstCaps *caps = gst_pad_get_current_caps(pad);
    if (caps == nullptr) {
      caps = gst_pad_query_caps(pad, nullptr);
    }
    if (caps == nullptr || gst_caps_is_empty(caps)) {
      if (caps != nullptr) {
        gst_caps_unref(caps);
      }
      return;
    }

    const GstStructure *structure = gst_caps_get_structure(caps, 0);
    const char *media = gst_structure_get_string(structure, "media");
    const char *encoding =
        gst_structure_get_string(structure, "encoding-name");
    const bool matches = media != nullptr && encoding != nullptr &&
                         std::string(media) == "video" &&
                         g_ascii_strcasecmp(
                             encoding,
                             config_.codec.rtp_encoding_name.c_str()) == 0;
    gst_caps_unref(caps);
    if (!matches) {
      return;
    }

    GstPad *sink_pad = gst_element_get_static_pad(depayloader_, "sink");
    if (sink_pad == nullptr) {
      set_failure("RTP depayloader has no sink pad");
      return;
    }
    if (!gst_pad_is_linked(sink_pad)) {
      const GstPadLinkReturn result = gst_pad_link(pad, sink_pad);
      if (result != GST_PAD_LINK_OK) {
        gst_object_unref(sink_pad);
        set_failure("failed to link RTSP video RTP pad, ret=" +
                    std::to_string(static_cast<int>(result)));
        return;
      }
      rtp_pad_linked_.store(true);
      std::cout << "[rtsp] linked " << config_.codec.rtp_encoding_name
                << " RTP pad\n";
    }
    gst_object_unref(sink_pad);
  }

  void feed_decoder() {
    while (!stop_requested_.load()) {
      GstSample *sample =
          gst_app_sink_try_pull_sample(appsink_, 100 * GST_MSECOND);
      if (sample == nullptr) {
        if (gst_app_sink_is_eos(appsink_)) {
          break;
        }
        continue;
      }
      GstBuffer *buffer = gst_sample_get_buffer(sample);
      GstMapInfo map{};
      if (buffer == nullptr || !gst_buffer_map(buffer, &map, GST_MAP_READ)) {
        gst_sample_unref(sample);
        set_failure("failed to map encoded GStreamer buffer");
        break;
      }
      if (map.size > static_cast<std::size_t>(
                         std::numeric_limits<std::int32_t>::max())) {
        gst_buffer_unmap(buffer, &map);
        gst_sample_unref(sample);
        set_failure("encoded access unit is too large for BSP decoder API");
        break;
      }

      lesson10::inspect_annex_b(reinterpret_cast<const char *>(map.data),
                                map.size, config_.codec.sp_type, metrics_.nal);
      ++metrics_.received_buffers;
      metrics_.received_bytes.fetch_add(map.size);
      const int ret = sp_decoder_set_image(
          decoder_, reinterpret_cast<char *>(map.data), 0,
          static_cast<std::int32_t>(map.size), 0);
      gst_buffer_unmap(buffer, &map);
      gst_sample_unref(sample);
      if (ret != 0) {
        set_failure("sp_decoder_set_image failed, ret=" +
                    std::to_string(ret) +
                    "; verify codec, resolution and SPS/PPS/VPS");
        break;
      }
      ++metrics_.decoder_submissions;
    }
    feeder_done_.store(true);
  }

  void drain_decoder() {
    constexpr std::uint64_t kDecoderHeadroom = 8;
    const std::size_t frame_size =
        static_cast<std::size_t>(config_.width) * config_.height * 3U / 2U;
    std::vector<char> frame(frame_size);
    while (!decoder_shutdown_.load()) {
      if (feeder_done_.load()) {
        break;
      }
      const std::uint64_t submitted = metrics_.decoder_submissions.load();
      const std::uint64_t decoded = metrics_.decoded_frames.load();
      if (submitted <= decoded + kDecoderHeadroom) {
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
        continue;
      }
      const int ret = sp_decoder_get_image(decoder_, frame.data());
      if (ret != 0) {
        if (decoder_shutdown_.load() || feeder_done_.load()) {
          break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
        continue;
      }

      const std::uint64_t frame_index = ++metrics_.decoded_frames;
      if (frame_index == 1) {
        const auto *bytes =
            reinterpret_cast<const std::uint8_t *>(frame.data());
        first_frame_crc_.store(lesson10::crc32(bytes, frame.size()));
        first_frame_crc_valid_.store(true);
        if (!config_.snapshot_path.empty()) {
          std::ofstream snapshot(config_.snapshot_path,
                                 std::ios::binary | std::ios::trunc);
          snapshot.write(frame.data(), static_cast<std::streamsize>(frame.size()));
          if (!snapshot) {
            set_failure("failed to write NV12 snapshot: " +
                        config_.snapshot_path);
            break;
          }
          std::cout << "[snapshot] wrote " << frame.size() << " bytes to "
                    << config_.snapshot_path << '\n';
        }
      }
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

  void stop_pipeline_and_threads() {
    request_stop();
    if (pipeline_ != nullptr && pipeline_started_) {
      gst_element_set_state(pipeline_, GST_STATE_NULL);
      pipeline_started_ = false;
    }
    if (feeder_thread_.joinable()) {
      feeder_thread_.join();
    }
    feeder_done_.store(true);
    if (drain_thread_.joinable()) {
      decoder_shutdown_.store(true);
      drain_thread_.join();
    }
  }

  void report_metrics(std::chrono::steady_clock::time_point now, bool final) {
    const std::uint64_t buffers = metrics_.received_buffers.load();
    const std::uint64_t bytes = metrics_.received_bytes.load();
    const double seconds =
        std::chrono::duration<double>(now - last_report_at_).count();
    const double buffer_rate =
        seconds > 0.0
            ? static_cast<double>(buffers - last_buffers_) / seconds
            : 0.0;
    const double bitrate =
        seconds > 0.0
            ? static_cast<double>(bytes - last_bytes_) * 8.0 / seconds /
                  1000000.0
            : 0.0;

    std::cout << (final ? "[summary]" : "[metrics]")
              << " received=" << buffers << " buffers"
              << " rate=" << std::fixed << std::setprecision(1) << buffer_rate
              << " buffer/s bitrate=" << std::setprecision(2) << bitrate
              << " Mbit/s submitted=" << metrics_.decoder_submissions.load();
    if (config_.headless) {
      std::cout << " decoded=" << metrics_.decoded_frames.load();
      if (first_frame_crc_valid_.load()) {
        std::cout << " first-crc32=0x" << std::hex << std::setw(8)
                  << std::setfill('0') << first_frame_crc_.load() << std::dec
                  << std::setfill(' ');
      }
    }
    std::cout << " NAL(vps/sps/pps/idr)=" << metrics_.nal.vps.load() << '/'
              << metrics_.nal.sps.load() << '/' << metrics_.nal.pps.load() << '/'
              << metrics_.nal.idr.load() << '\n';
    last_report_at_ = now;
    last_buffers_ = buffers;
    last_bytes_ = bytes;
  }

  void cleanup() {
    stop_pipeline_and_threads();
    display_path_.cleanup();

    if (decoder_started_) {
      sp_stop_decode(decoder_);
      decoder_started_ = false;
    }
    if (decoder_ != nullptr) {
      sp_release_decoder_module(decoder_);
      decoder_ = nullptr;
    }
    if (bus_ != nullptr) {
      gst_object_unref(bus_);
      bus_ = nullptr;
    }
    if (pipeline_ != nullptr) {
      gst_object_unref(pipeline_);
      pipeline_ = nullptr;
    }
    source_ = nullptr;
    depayloader_ = nullptr;
    parser_ = nullptr;
    caps_filter_ = nullptr;
    appsink_element_ = nullptr;
    appsink_ = nullptr;
  }

  Config config_;
  Metrics metrics_;
  lesson10::DisplayPath display_path_;

  void *decoder_ = nullptr;
  bool decoder_started_ = false;

  GstElement *pipeline_ = nullptr;
  GstElement *source_ = nullptr;
  GstElement *depayloader_ = nullptr;
  GstElement *parser_ = nullptr;
  GstElement *caps_filter_ = nullptr;
  GstElement *appsink_element_ = nullptr;
  GstAppSink *appsink_ = nullptr;
  GstBus *bus_ = nullptr;
  bool pipeline_started_ = false;

  std::atomic<bool> stop_requested_{false};
  std::atomic<bool> failed_{false};
  std::atomic<bool> feeder_done_{false};
  std::atomic<bool> decoder_shutdown_{false};
  std::atomic<bool> rtp_pad_linked_{false};
  std::atomic<bool> first_frame_crc_valid_{false};
  std::atomic<std::uint32_t> first_frame_crc_{0};
  std::mutex error_mutex_;
  std::string first_error_;
  std::thread feeder_thread_;
  std::thread drain_thread_;
  std::chrono::steady_clock::time_point started_at_{};
  std::chrono::steady_clock::time_point last_report_at_{};
  std::uint64_t last_buffers_ = 0;
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
      RtspDecoderClient client(std::move(config));
      ok = client.initialize() && client.run();
    }
    gst_deinit();
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
  } catch (const std::exception &error) {
    std::cerr << "[error] " << error.what() << '\n';
    return EXIT_FAILURE;
  }
}
