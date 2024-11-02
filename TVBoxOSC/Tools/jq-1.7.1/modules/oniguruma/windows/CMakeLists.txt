
add_executable(testc_windows testc.c)
target_link_libraries(testc_windows onig)
if(NOT MSVC)
  target_compile_options(testc_windows
    PRIVATE --input-charset=cp932 --exec-charset=cp932
  )
endif(NOT MSVC)
