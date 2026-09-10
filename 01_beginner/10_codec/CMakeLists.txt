cmake_minimum_required(VERSION 3.16)

project(lesson10_codec_rtsp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)
find_package(PkgConfig REQUIRED)
find_library(SPCDEV_LIBRARY NAMES spcdev REQUIRED)
pkg_check_modules(GSTREAMER REQUIRED IMPORTED_TARGET
  gstreamer-1.0
  gstreamer-app-1.0
  gstreamer-rtsp-1.0
  gstreamer-rtsp-server-1.0
)

add_library(codec_common STATIC
  src/codec_common.cpp
)

target_include_directories(codec_common PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_options(codec_common PRIVATE
  -Wall
  -Wextra
  -Wpedantic
)

target_link_libraries(codec_common PUBLIC
  ${SPCDEV_LIBRARY}
  Threads::Threads
)

add_executable(codec_rtsp_server
  src/codec_rtsp_server.cpp
)

add_executable(codec_rtsp_client
  src/codec_rtsp_client.cpp
)

foreach(target codec_rtsp_server codec_rtsp_client)
  target_compile_options(${target} PRIVATE
    -Wall
    -Wextra
    -Wpedantic
  )
  target_link_libraries(${target} PRIVATE
    codec_common
    PkgConfig::GSTREAMER
  )
endforeach()

install(TARGETS codec_rtsp_server codec_rtsp_client
  RUNTIME DESTINATION bin
)
