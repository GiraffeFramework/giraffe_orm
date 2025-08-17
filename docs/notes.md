- Query.latest() has 3 options:
    1. You could provide no argument, the first field matching the type Date will be picked and cached (so used from then on when no argument is used). This caching is on program level so only lives as long as the program.
    2. You could provide a field as argument, when this field is a date, it will be used and overwrite the cache.
    3. You could provide a field name as argument, when this leads to a field date, the cached date field will also be overwritten