# Evolution Summary

**Generated:** 2026-05-28T21:29:06.579142+00:00
**Total cycles:** 203
**Score range:** 17.0 – 39.0
**Average score:** 30.9
**Best:** Cycle 32 (caching_layer) = 39.0
**Worst:** Cycle 2 (flask_api) = 17.0

**Trend:** upward (first 10 avg=25.8, last 10 avg=28.7)

## Benchmark Usage

| Benchmark | Cycles |
|-----------|--------|
| math_library | 37 |
| cli_task_manager | 33 |
| flask_api | 31 |
| file_indexer | 31 |
| data_pipeline | 29 |
| caching_layer | 23 |
| async_web_scraper | 19 |

## Mutation Usage

| Operator | Uses |
|----------|------|
| mutation | 127 |
| crossover | 76 |

## Cycle History

| Cycle | Score | Benchmark | Mutation | Tests | Test Qual | Hidden | Files | Tokens |
|-------|-------|-----------|----------|-------|-----------|--------|-------|--------|
|    0 |  19.0 | flask_api    | mutation | Y |   4.0 | N |  22 |  5302 |
|    1 |  21.0 | cli_task_manager | mutation | Y |   5.0 | N |   5 |  5900 |
|    2 |  17.0 | flask_api    | mutation | Y |   4.0 | N |  25 |  7160 |
|    3 |  17.0 | file_indexer | crossover | Y |   4.0 | N |  15 |  2342 |
|    4 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  23 |  3752 |
|    5 |  19.0 | flask_api    | crossover | Y |   4.0 | N |  27 |  3904 |
|    6 |  36.0 | async_web_scraper | mutation | Y |   5.0 | N |  19 |  5253 |
|    7 |  36.0 | cli_task_manager | crossover | Y |   5.0 | N |  31 |  5516 |
|    8 |  21.0 | caching_layer | crossover | Y |   5.0 | N |  21 |  3909 |
|    9 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  21 |  3152 |
|   10 |  34.0 | flask_api    | crossover | Y |   4.0 | N |  19 |  3586 |
|   11 |  36.0 | data_pipeline | crossover | Y |   5.0 | N |  42 |  5785 |
|   12 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |   8 |  5863 |
|   13 |  36.0 | async_web_scraper | crossover | Y |   5.0 | N |  26 |  5622 |
|   14 |  34.0 | flask_api    | crossover | Y |   4.0 | N |  22 |  7247 |
|   15 |  36.0 | caching_layer | crossover | Y |   5.0 | N |  29 |  5354 |
|   16 |  19.0 | file_indexer | mutation | Y |   4.0 | N |  27 |  6280 |
|   17 |  36.0 | data_pipeline | crossover | Y |   5.0 | N |  33 |  4691 |
|   18 |  36.0 | math_library | mutation | Y |   5.0 | N |   6 |  6259 |
|   19 |  21.0 | math_library | mutation | Y |   5.0 | N |  19 |  4906 |
|   20 |  34.0 | flask_api    | mutation | Y |   4.0 | N |  26 |  3407 |
|   21 |  34.0 | file_indexer | mutation | Y |   4.0 | N |  21 |  6079 |
|   22 |  21.0 | math_library | mutation | Y |   5.0 | N |  25 |  5724 |
|   23 |  19.0 | file_indexer | crossover | Y |   4.0 | N |  38 |  7079 |
|   24 |  32.0 | flask_api    | crossover | Y |   4.0 | N |  25 |  4516 |
|   25 |  21.0 | async_web_scraper | crossover | Y |   5.0 | N |  31 |  6459 |
|   26 |  21.0 | data_pipeline | mutation | Y |   5.0 | N |  20 |  4156 |
|   27 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  29 |  5901 |
|   28 |  21.0 | math_library | crossover | Y |   5.0 | N |  29 |  7117 |
|   29 |  21.0 | math_library | mutation | Y |   5.0 | N |  32 |  9199 |
|   30 |  24.0 | data_pipeline | mutation | Y |   5.0 | N |  25 |  4412 |
|   31 |  32.0 | file_indexer | mutation | Y |   4.0 | N |  25 |  3227 |
|   32 |  39.0 | caching_layer | mutation | Y |   5.0 | N |  25 |  5701 |
|   33 |  19.0 | flask_api    | mutation | Y |   4.0 | N |  32 |  9160 |
|   34 |  36.0 | async_web_scraper | crossover | Y |   5.0 | N |  29 |  7363 |
|   35 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   6 |  4532 |
|   36 |  19.0 | math_library | mutation | Y |   5.0 | N |  16 |  1832 |
|   37 |  21.0 | math_library | crossover | Y |   5.0 | N |  26 |  5835 |
|   38 |  19.0 | math_library | mutation | Y |   5.0 | N |  28 |  5014 |
|   39 |  34.0 | data_pipeline | crossover | Y |   5.0 | N |  26 |  4725 |
|   40 |  34.0 | math_library | mutation | Y |   5.0 | N |  28 |  5449 |
|   41 |  17.0 | file_indexer | crossover | Y |   4.0 | N |  22 |  3282 |
|   42 |  34.0 | flask_api    | crossover | Y |   4.0 | N |  20 |  4327 |
|   43 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |  27 |  5400 |
|   44 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  23 |  5266 |
|   45 |  34.0 | file_indexer | mutation | Y |   4.0 | N |  20 |  4793 |
|   46 |  17.0 | file_indexer | crossover | Y |   4.0 | N |  30 |  3423 |
|   47 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  23 |  4152 |
|   48 |  34.0 | file_indexer | mutation | Y |   4.0 | N |  24 |  4974 |
|   49 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |  20 |  5131 |
|   50 |  19.0 | flask_api    | mutation | Y |   4.0 | N |  17 |  4921 |
|   51 |  19.0 | data_pipeline | mutation | Y |   5.0 | N |  33 |  5399 |
|   52 |  34.0 | flask_api    | mutation | Y |   4.0 | N |  26 |  8087 |
|   53 |  32.0 | file_indexer | crossover | Y |   4.0 | N |  31 |  4994 |
|   54 |  17.0 | flask_api    | crossover | Y |   4.0 | N |  29 |  8049 |
|   55 |  32.0 | flask_api    | crossover | Y |   4.0 | N |  25 |  8134 |
|   56 |  19.0 | math_library | crossover | Y |   5.0 | N |  28 |  7356 |
|   57 |  17.0 | flask_api    | crossover | Y |   4.0 | N |  33 |  4499 |
|   58 |  21.0 | math_library | mutation | Y |   5.0 | N |  27 |  5980 |
|   59 |  36.0 | cli_task_manager | mutation | Y |   5.0 | N |  20 |  3699 |
|   60 |  19.0 | async_web_scraper | mutation | Y |   5.0 | N |  17 |  2076 |
|   61 |  19.0 | caching_layer | crossover | Y |   5.0 | N |  28 |  4623 |
|   62 |  21.0 | math_library | crossover | Y |   5.0 | N |  22 |  3835 |
|   63 |  34.0 | file_indexer | mutation | Y |   4.0 | N |  32 |  6913 |
|   64 |  21.0 | caching_layer | crossover | Y |   5.0 | N |  19 |  2080 |
|   65 |  34.0 | file_indexer | mutation | Y |   4.0 | N |  28 |  8851 |
|   66 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |  40 |  8362 |
|   67 |  32.0 | file_indexer | crossover | Y |   4.0 | N |  31 |  6248 |
|   68 |  36.0 | cli_task_manager | crossover | Y |   5.0 | N |  32 |  7806 |
|   69 |  19.0 | data_pipeline | mutation | Y |   5.0 | N |  20 |  3333 |
|   70 |  32.0 | file_indexer | crossover | Y |   4.0 | N |  24 |  5213 |
|   71 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |  23 |  7852 |
|   72 |  36.0 | math_library | mutation | Y |   5.0 | N |  25 |  6720 |
|   73 |  36.0 | async_web_scraper | crossover | Y |   5.0 | N |  21 |  4733 |
|   74 |  19.0 | math_library | crossover | Y |   5.0 | N |  28 |  7391 |
|   75 |  36.0 | async_web_scraper | mutation | Y |   5.0 | N |   6 |  5636 |
|   76 |  34.0 | flask_api    | mutation | Y |   4.0 | N |  18 |  5368 |
|   77 |  17.0 | flask_api    | mutation | Y |   4.0 | N |  35 |  6044 |
|   78 |  36.0 | data_pipeline | mutation | Y |   5.0 | N |  37 |  9583 |
|   79 |  37.0 | caching_layer | mutation | Y |   5.0 | N |  14 |  1660 |
|   80 |  36.0 | math_library | mutation | Y |   5.0 | N |  37 |  6960 |
|   81 |  36.0 | cli_task_manager | mutation | Y |   5.0 | N |  31 |  6947 |
|   82 |  21.0 | math_library | crossover | Y |   5.0 | N |  24 |  8294 |
|   83 |  21.0 | cli_task_manager | crossover | Y |   5.0 | N |  24 |  6312 |
|   84 |  19.0 | caching_layer | mutation | Y |   5.0 | N |  29 |  5752 |
|   85 |  19.0 | file_indexer | mutation | Y |   4.0 | N |  29 |  3881 |
|   86 |  32.0 | file_indexer | crossover | Y |   4.0 | N |  20 |  3105 |
|   87 |  36.0 | math_library | mutation | Y |   5.0 | N |  20 |  2920 |
|   88 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|   89 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|   90 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|   91 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|   92 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|   93 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|   94 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|   95 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|   96 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|   97 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|   98 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|   99 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  100 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  101 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  102 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  103 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  104 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  105 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  106 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  107 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  108 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  109 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  110 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  111 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  112 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  113 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  114 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  115 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  116 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  117 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  118 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  119 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  120 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  121 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  122 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  123 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  124 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  125 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  126 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  127 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  128 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  129 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  130 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  131 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  132 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  133 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  134 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  135 |  34.0 | async_web_scraper | crossover | Y |   5.0 | N |   3 |     1 |
|  136 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  137 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  138 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  139 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  140 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  141 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  142 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  143 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  144 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  145 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  146 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  147 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  148 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  149 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  150 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  151 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  152 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  153 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  154 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  155 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  156 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  157 |  34.0 | data_pipeline | crossover | Y |   5.0 | N |   3 |     1 |
|  158 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  159 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  160 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  161 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  162 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  163 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  164 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  165 |  34.0 | caching_layer | mutation | Y |   5.0 | N |   3 |     1 |
|  166 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  167 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  168 |  32.0 | flask_api    | mutation | Y |   4.0 | N |   3 |     1 |
|  169 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  170 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  171 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  172 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  173 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  174 |  32.0 | file_indexer | mutation | Y |   4.0 | N |   3 |     1 |
|  175 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  176 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  177 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  178 |  34.0 | async_web_scraper | mutation | Y |   5.0 | N |   3 |     1 |
|  179 |  34.0 | async_web_scraper | crossover | Y |   5.0 | N |   3 |     1 |
|  180 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  181 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |   3 |     1 |
|  182 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |   3 |     1 |
|  183 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  184 |  34.0 | math_library | mutation | Y |   5.0 | N |   3 |     1 |
|  185 |  34.0 | cli_task_manager | crossover | Y |   5.0 | N |   3 |     1 |
|  186 |  32.0 | flask_api    | crossover | Y |   4.0 | N |   3 |     1 |
|  187 |  32.0 | file_indexer | crossover | Y |   4.0 | N |   3 |     1 |
|  188 |  34.0 | data_pipeline | crossover | Y |   5.0 | N |   3 |     1 |
|  189 |  34.0 | caching_layer | crossover | Y |   5.0 | N |   3 |     1 |
|  190 |  34.0 | data_pipeline | crossover | Y |   5.0 | N |   3 |     1 |
|  191 |  34.0 | async_web_scraper | crossover | Y |   5.0 | N |   3 |     1 |
|  192 |  34.0 | math_library | crossover | Y |   5.0 | N |   3 |     1 |
|  193 |  21.0 | async_web_scraper | mutation | Y |   5.0 | N |   9 |  5830 |
|  194 |  34.0 | data_pipeline | mutation | Y |   5.0 | N |  32 |  9242 |
|  195 |  36.0 | math_library | crossover | Y |   5.0 | N |  41 |  7100 |
|  196 |  36.0 | async_web_scraper | mutation | Y |   5.0 | N |  21 |  4626 |
|  197 |  19.0 | cli_task_manager | crossover | Y |   5.0 | N |  25 |  5661 |
|  198 |  19.0 | math_library | mutation | Y |   5.0 | N |  19 |  3695 |
|  199 |  17.0 | file_indexer | mutation | Y |   4.0 | N |  33 |  7251 |
|  200 |  35.0 | math_library | mutation | Y |   5.0 | N |  20 |  4795 |
|  201 |  36.0 | cli_task_manager | mutation | Y |   5.0 | N |  30 |  4853 |
|  202 |  34.0 | cli_task_manager | mutation | Y |   5.0 | N |  25 |  5657 |

## Metadata

- **Generated projects:** `generated_projects/`
- **Archives:** `experiments/projects/`
- **Mutation weights:** `memory/mutation_weights.json`
- **Population:** `population/population.json`
