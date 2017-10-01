30.09.17

  + Write tests for class_directory_3

  + Create a class ClassEntryLinked that will bind info about ClassEntry that
  can be obtained from array of DllEntries

ClassHeader.dll_index is the index of DllEntry containing the class.

  + Add method .link() to ClassEntry that should return instance of ClassEntryLinked.

01.10.17

  - Write tests for ClassEntry.link

  - Remove redundant attributes from derived classes

  ClassName does not need to hold the original binary value, as well as
  the nesting level, idn, length, storage_type and so on.

  Every derived class from class_directory_3 and dll_directory has this
  problem.

  It may be interesting to measure the execution time of tests before and after
  the task is completed.
