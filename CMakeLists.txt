cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(AlgoAnalysisSPLA)
include(FetchContent)

FetchContent_Declare(
  spla
  GIT_REPOSITORY https://github.com/Parzival-05/spla
  GIT_TAG "2ae96390bf6f09563667483ddc3071ba157ac9cf" 
  GIT_SHALLOW TRUE
  GIT_PROGRESS ON
  SYSTEM
)

FetchContent_MakeAvailable(spla)
