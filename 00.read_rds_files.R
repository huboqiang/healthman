#!/cluster/apps/anaconda3/2020.02/envs/R-4.2.1/bin/Rscript
load_libraries <- function() {
  pkgs <- c(
    "fs", "tidyverse", "futile.logger", "configr", "stringr", "optparse",
    "Seurat", "jhuanglabscell", "jhtools"
  )
  for (pkg in pkgs) {
    suppressPackageStartupMessages(library(pkg, character.only = T))
  }
}
# dependencies
load_libraries()


df11 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/detail_2021.rds")
df12 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/main_2021.rds")
df21 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/detail_2022.rds")
df22 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/main_2022.rds")
df31 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/detail_2023.rds")
df32 <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/main_2023.rds")


write.csv(df11, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/detail_2021.csv", row.names = FALSE)
write.csv(df12, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/main_2021.csv", row.names = FALSE)
write.csv(df21, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/detail_2022.csv", row.names = FALSE)
write.csv(df22, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/main_2022.csv", row.names = FALSE)
write.csv(df31, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/detail_2023.csv", row.names = FALSE)
write.csv(df32, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/main_2023.csv", row.names = FALSE)

# project <- "healthman"
# species <- "human"

# workdir <- glue("~/projects/{project}/analysis/liuzhong/{species}/clinical/overall_barplot") %>% checkdir()
# setwd(workdir)
# rds_dir <- "/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds"
# df_all <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/exam_123.rds")
# df_3y <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/exam_three_years_123.rds")


# # 203657    415
# exam_data <- read_rds(glue::glue("{rds_dir}/exam_123.rds")) %>% 
#   separate(col = exam_date, into = c("year", "month", "day"), sep = "-")
# write.csv(exam_data, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/exam_123.csv", row.names = FALSE)

# # 33270   413
# exam_data_paired <- read_rds(glue::glue("{rds_dir}/exam_three_years_123.rds")) 
# write.csv(exam_data_paired, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/exam_three_years_123.csv", row.names = FALSE)




# library(lubridate)

# get_num_part_of_val <- function(x) {
#   if (!is.character(x)) {
#     return(x)
#   }

#   l_val <- str_split(x, ";")[[1]]
#   l_res <- lapply(l_val, function(val) {
#     val <- str_remove_all(val, "干扰")
#     val <- str_remove_all(val, "<")
#     val <- str_remove_all(val, ">")
#     return(val)
#   })

#   l_res <- lapply(l_res, function(val) {
#     if (is.na(as.numeric(val))) {
#       return(NA)
#     } else {
#       return(as.numeric(val))
#     }
#   })
#   return(mean(unlist(l_res), na.rm = TRUE))
# }

# # df <- read.csv("/cluster/home/bqhu_jh/projects/healthman/analysis/2020s.csv", stringsAsFactors = FALSE)
# df <- readRDS("/cluster/home/jhuang/projects/healthman/analysis/liuzhong/human/clinical/rds/exam_123.rds")
# df_meta <- read.csv("/cluster/home/bqhu_jh/projects/liuzhong/analysis/detail_202304-peopleXfeatures_numeric-withMonth_metadata.csv", stringsAsFactors = FALSE)

# df_meta_sub <- df_meta %>% dplyr::filter(TYPE == "NUMBER")
# col_name <- paste0("v", df_meta_sub$XIANGMUBM)
# df_sub <- df[, col_name]

# year <- year(parse_date_time(df$exam_date, orders = c("%Y-%m-%d", "%Y/%m/%d")))
# arr <- apply(df_sub, c(1, 2), get_num_part_of_val)



# df_result <- as.data.frame(arr) %>% set_names(df_meta_sub$name)
# df_result$year <- year

# df_result <- df_result %>%
#   select(birthday = birthday.x, exam_date, exam_id, gender, sample_id, age_day = age_day.x, year, everything()) %>%
#   left_join(df %>% select(birthday, exam_date, exam_id, gender, sample_id), by = c("birthday", "exam_date", "exam_id", "gender", "sample_id")) %>%
#   mutate(age_day = as.numeric(difftime(parse_date_time(exam_date, orders = c("%Y-%m-%d", "%Y/%m/%d")), parse_date_time(birthday, orders = c("%Y-%m-%d", "%Y/%m/%d")), units = "days"))) %>%
#   select(birthday, exam_date, exam_id, gender, sample_id, age_day, year, everything())

# write.csv(df_result, file = "/cluster/home/bqhu_jh/projects/healthman/analysis/2021-2023_num.csv", row.names = FALSE)
