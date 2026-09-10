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

#pragma once

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <string>

#include "sp_codec.h"

namespace lesson10 {

void install_signal_handlers();
bool signal_stop_requested();

int parse_int(const std::string &option, const std::string &value);

struct CodecSpec {
  int sp_type = SP_ENCODER_H264;
  std::string name = "h264";
  std::string media_type = "video/x-h264";
  std::string parser = "h264parse";
  std::string payloader = "rtph264pay";
  std::string depayloader = "rtph264depay";
  std::string rtp_encoding_name = "H264";
};

CodecSpec codec_spec_from_name(const std::string &name);

enum class BoardFamily { kX5, kS100, kUnknown };

struct PlatformProfile {
  BoardFamily family = BoardFamily::kUnknown;
  std::string model = "unknown";
  int default_display_channel = 1;
  bool display_resolution_is_list = true;
};

PlatformProfile detect_platform();

struct DisplayConfig {
  int vps_pipe_id = 1;
  int display_channel = -1;
  int display_width = 0;
  int display_height = 0;
};

class DisplayPath {
 public:
  DisplayPath() = default;
  ~DisplayPath();

  DisplayPath(const DisplayPath &) = delete;
  DisplayPath &operator=(const DisplayPath &) = delete;

  bool initialize(void *decoder, int stream_width, int stream_height,
                  const DisplayConfig &config);
  void cleanup();

  const std::string &error() const { return error_; }
  int width() const { return display_width_; }
  int height() const { return display_height_; }
  int channel() const { return display_channel_; }

 private:
  bool fail(const std::string &message);

  void *decoder_ = nullptr;
  void *display_ = nullptr;
  void *display_vps_ = nullptr;
  int display_width_ = 0;
  int display_height_ = 0;
  int display_channel_ = 0;
  bool display_started_ = false;
  bool display_vps_open_ = false;
  bool decoder_vps_bound_ = false;
  bool vps_display_bound_ = false;
  std::string error_;
};

struct NalMetrics {
  std::atomic<std::uint64_t> vps{0};
  std::atomic<std::uint64_t> sps{0};
  std::atomic<std::uint64_t> pps{0};
  std::atomic<std::uint64_t> idr{0};
};

void inspect_annex_b(const char *data, std::size_t size, int codec,
                     NalMetrics &metrics);

std::uint32_t crc32(const std::uint8_t *data, std::size_t size);

}  // namespace lesson10
