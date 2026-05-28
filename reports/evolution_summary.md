# Evolution Summary

**Generated:** 2026-05-28T19:23:40.051482+00:00
**Total cycles:** 31
**Score range:** 17.0 – 36.0
**Average score:** 27.9
**Best:** Cycle 4 (data_pipeline) = 36.0
**Worst:** Cycle 2 (flask_api) = 17.0

**Trend:** flat (first 10 avg=25.8, last 10 avg=25.0)

## Benchmark Usage

| Benchmark | Cycles |
|-----------|--------|
| data_pipeline | 8 |
| flask_api | 7 |
| math_library | 5 |
| file_indexer | 4 |
| async_web_scraper | 3 |
| cli_task_manager | 2 |
| caching_layer | 2 |

## Mutation Usage

| Operator | Uses |
|----------|------|
| mutation | 17 |
| crossover | 14 |

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

## Metadata

- **Generated projects:** `generated_projects/`
- **Archives:** `experiments/projects/`
- **Mutation weights:** `memory/mutation_weights.json`
- **Population:** `population/population.json`
