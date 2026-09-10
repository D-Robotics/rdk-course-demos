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

#include "codec_common.hpp"

#include <algorithm>
#include <csignal>
#include <fstream>
#include <limits>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <vector>

#include "sp_display.h"
#include "sp_sys.h"
#include "sp_vio.h"

namespace lesson10 {
namespace {

volatile std::sig_atomic_t g_signal_stop = 0;

void signal_handler(int) { g_signal_stop = 1; }

struct DisplayMode {
  int width = 0;
  int height = 0;
};

std::string read_model() {
  std::ifstream input("/proc/device-tree/model", std::ios::binary);
  if (!input) {
    return "unknown";
  }
  std::ostringstream contents;
  contents << input.rdbuf();
  std::string model = contents.str();
  model.erase(std::remove(model.begin(), model.end(), '\0'), model.end());
  return model.empty() ? "unknown" : model;
}

std::optional<DisplayMode> query_display_mode(const PlatformProfile &profile,
                                              int stream_width,
                                              int stream_height) {
  if (!profile.display_resolution_is_list) {
    DisplayMode mode;
    sp_get_display_resolution(&mode.width, &mode.height);
    if (mode.width > 0 && mode.height > 0) {
      return mode;
    }
    return std::nullopt;
  }

  constexpr std::size_t kMaxModes = 20;
  int widths[kMaxModes] = {};
  int heights[kMaxModes] = {};
  sp_get_display_resolution(widths, heights);

  std::vector<DisplayMode> modes;
  for (std::size_t i = 0; i < kMaxModes; ++i) {
    if (widths[i] <= 0 || heights[i] <= 0) {
      break;
    }
    modes.push_back({widths[i], heights[i]});
  }
  if (modes.empty()) {
    return std::nullopt;
  }

  const auto exact = std::find_if(
      modes.begin(), modes.end(), [&](const DisplayMode &mode) {
        return mode.width == stream_width && mode.height == stream_height;
      });
  if (exact != modes.end()) {
    return *exact;
  }

  std::optional<DisplayMode> largest_fitting;
  std::int64_t largest_area = -1;
  for (const DisplayMode &mode : modes) {
    if (mode.width <= stream_width && mode.height <= stream_height) {
      const std::int64_t area =
          static_cast<std::int64_t>(mode.width) * mode.height;
      if (area > largest_area) {
        largest_area = area;
        largest_fitting = mode;
      }
    }
  }
  return largest_fitting.has_value() ? largest_fitting
                                     : std::optional<DisplayMode>(modes.front());
}

}  // namespace

void install_signal_handlers() {
  std::signal(SIGINT, signal_handler);
  std::signal(SIGTERM, signal_handler);
}

bool signal_stop_requested() { return g_signal_stop != 0; }

int parse_int(const std::string &option, const std::string &value) {
  std::size_t parsed = 0;
  long number = 0;
  try {
    number = std::stol(value, &parsed, 10);
  } catch (const std::exception &) {
    throw std::runtime_error(option + " expects an integer, got: " + value);
  }
  if (parsed != value.size() || number < std::numeric_limits<int>::min() ||
      number > std::numeric_limits<int>::max()) {
    throw std::runtime_error(option + " expects an integer, got: " + value);
  }
  return static_cast<int>(number);
}

CodecSpec codec_spec_from_name(const std::string &name) {
  if (name == "h264") {
    return {};
  }
  if (name == "h265") {
    CodecSpec spec;
    spec.sp_type = SP_ENCODER_H265;
    spec.name = "h265";
    spec.media_type = "video/x-h265";
    spec.parser = "h265parse";
    spec.payloader = "rtph265pay";
    spec.depayloader = "rtph265depay";
    spec.rtp_encoding_name = "H265";
    return spec;
  }
  throw std::runtime_error("--codec must be h264 or h265");
}

PlatformProfile detect_platform() {
  PlatformProfile profile;
  profile.model = read_model();
  if (profile.model.find("S100") != std::string::npos) {
    profile.family = BoardFamily::kS100;
    profile.default_display_channel = 11;
    profile.display_resolution_is_list = false;
  } else if (profile.model.find("X5") != std::string::npos) {
    profile.family = BoardFamily::kX5;
    profile.default_display_channel = 1;
    profile.display_resolution_is_list = true;
  }
  return profile;
}

DisplayPath::~DisplayPath() { cleanup(); }

bool DisplayPath::initialize(void *decoder, int stream_width,
                             int stream_height,
                             const DisplayConfig &config) {
  decoder_ = decoder;
  const PlatformProfile profile = detect_platform();

  if (config.display_width > 0 && config.display_height > 0) {
    display_width_ = config.display_width;
    display_height_ = config.display_height;
  } else {
    const auto mode = query_display_mode(profile, stream_width, stream_height);
    if (!mode.has_value()) {
      return fail("no active display mode; connect HDMI or use --headless");
    }
    display_width_ = mode->width;
    display_height_ = mode->height;
  }
  display_channel_ = config.display_channel >= 0
                         ? config.display_channel
                         : profile.default_display_channel;

  display_ = sp_init_display_module();
  display_vps_ = sp_init_vio_module();
  if (display_ == nullptr || display_vps_ == nullptr) {
    return fail("failed to create Display/VPS module objects");
  }

  int ret = sp_start_display(display_, display_channel_, display_width_,
                             display_height_);
  if (ret != 0) {
    return fail("sp_start_display failed, ret=" + std::to_string(ret));
  }
  display_started_ = true;

  int output_width = display_width_;
  int output_height = display_height_;
  ret = sp_open_vps(display_vps_, config.vps_pipe_id, 1, SP_VPS_SCALE,
                    stream_width, stream_height, &output_width, &output_height,
                    nullptr, nullptr, nullptr, nullptr, nullptr);
  if (ret != 0) {
    return fail("sp_open_vps failed, ret=" + std::to_string(ret));
  }
  display_vps_open_ = true;

  ret = sp_module_bind(decoder_, SP_MTYPE_DECODER, display_vps_, SP_MTYPE_VIO);
  if (ret != 0) {
    return fail("sp_module_bind(decoder, VPS) failed, ret=" +
                std::to_string(ret));
  }
  decoder_vps_bound_ = true;

  ret = sp_module_bind(display_vps_, SP_MTYPE_VIO, display_, SP_MTYPE_DISPLAY);
  if (ret != 0) {
    return fail("sp_module_bind(VPS, display) failed, ret=" +
                std::to_string(ret));
  }
  vps_display_bound_ = true;
  return true;
}

void DisplayPath::cleanup() {
  if (vps_display_bound_) {
    sp_module_unbind(display_vps_, SP_MTYPE_VIO, display_, SP_MTYPE_DISPLAY);
    vps_display_bound_ = false;
  }
  if (decoder_vps_bound_) {
    sp_module_unbind(decoder_, SP_MTYPE_DECODER, display_vps_, SP_MTYPE_VIO);
    decoder_vps_bound_ = false;
  }
  if (display_started_) {
    sp_stop_display(display_);
    display_started_ = false;
  }
  if (display_vps_open_) {
    sp_vio_close(display_vps_);
    display_vps_open_ = false;
  }
  if (display_ != nullptr) {
    sp_release_display_module(display_);
    display_ = nullptr;
  }
  if (display_vps_ != nullptr) {
    sp_release_vio_module(display_vps_);
    display_vps_ = nullptr;
  }
  decoder_ = nullptr;
}

bool DisplayPath::fail(const std::string &message) {
  error_ = message;
  cleanup();
  return false;
}

void inspect_annex_b(const char *data, std::size_t size, int codec,
                     NalMetrics &metrics) {
  const auto *bytes = reinterpret_cast<const std::uint8_t *>(data);
  std::size_t position = 0;
  while (position + 3 < size) {
    std::size_t header = size;
    for (std::size_t i = position; i + 3 < size; ++i) {
      if (bytes[i] == 0 && bytes[i + 1] == 0 && bytes[i + 2] == 1) {
        header = i + 3;
        break;
      }
      if (i + 4 < size && bytes[i] == 0 && bytes[i + 1] == 0 &&
          bytes[i + 2] == 0 && bytes[i + 3] == 1) {
        header = i + 4;
        break;
      }
    }
    if (header >= size) {
      break;
    }

    if (codec == SP_ENCODER_H264) {
      const std::uint8_t type = bytes[header] & 0x1fU;
      if (type == 7) {
        ++metrics.sps;
      } else if (type == 8) {
        ++metrics.pps;
      } else if (type == 5) {
        ++metrics.idr;
      }
    } else {
      const std::uint8_t type = (bytes[header] >> 1U) & 0x3fU;
      if (type == 32) {
        ++metrics.vps;
      } else if (type == 33) {
        ++metrics.sps;
      } else if (type == 34) {
        ++metrics.pps;
      } else if (type == 19 || type == 20 || type == 21) {
        ++metrics.idr;
      }
    }
    position = header + 1;
  }
}

std::uint32_t crc32(const std::uint8_t *data, std::size_t size) {
  std::uint32_t crc = 0xffffffffU;
  for (std::size_t i = 0; i < size; ++i) {
    crc ^= data[i];
    for (int bit = 0; bit < 8; ++bit) {
      const std::uint32_t mask = 0U - (crc & 1U);
      crc = (crc >> 1U) ^ (0xedb88320U & mask);
    }
  }
  return ~crc;
}

}  // namespace lesson10
