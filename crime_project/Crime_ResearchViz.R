library(tidyverse)
library(ggmap)
library(viridis)

df <- read_csv("crime2024.csv")


#-------------------------------------------------------------------------------
#Cleaning data for visualizations
df_clean <- df %>%
  filter(!is.na(LATITUDE), !is.na(LONGITUDE), !is.na(OFFENSE))


top_offenses <- df_clean %>%
  count(OFFENSE, sort = TRUE) %>%
  slice_max(n, n = 3) %>%
  pull(OFFENSE)

df_top <- df_clean %>%
  filter(OFFENSE %in% top_offenses)

dc_bbox <- c(left = -77.12, bottom = 38.79, right = -76.90, top = 38.99)


#-------------------------------------------------------------------------------
#My API key to get the map background

api_key <- Sys.getenv("STADIA_API_KEY")
register_stadiamaps(key = api_key)

dc_map <- get_stadiamap(bbox = dc_bbox, zoom = 12, maptype = "stamen_toner_lite")

#-------------------------------------------------------------------------------
#Overall Map for top 3 crimes.

ggmap(dc_map) +
  geom_point(data = df_top,
             aes(x = LONGITUDE, y = LATITUDE, color = OFFENSE),
             alpha = 0.5, size = 1.2) +
  scale_color_brewer(palette = "Dark2") +
  labs(
    title = "Top 3 Offense Types in Washington D.C. (2024)",
    subtitle = "Crime locations plotted by longitude and latitude",
    x = "Longitude", y = "Latitude", color = "Offense Type"
  ) + theme_minimal()


#-------------------------------------------------------------------------------
#Bar chart of offenses committed per ward. 
df_top %>%
  filter(!is.na(WARD)) %>%
  count(WARD, OFFENSE) %>%
  ggplot(aes(x = factor(WARD), y = n, fill = OFFENSE)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Crime Count by Ward and Offense Type",
       x = "Ward", y = "Number of Crimes", fill = "Offense") +
  theme_minimal()



#-------------------------------------------------------------------------------
#Density map of crime hot spots per area.
ggmap(dc_map) +
  stat_density2d(
    data = df_top,
    aes(x = LONGITUDE, y = LATITUDE, fill = ..level..),
    geom = "polygon", alpha = 0.6, bins = 20
  ) +
  scale_fill_viridis_c(option = "inferno") +
  facet_wrap(~ OFFENSE) +
  labs(
    title = "Crime Hotspots in Washington D.C.",
    subtitle = "Density map by offense type",
    fill = "Crime Density"
  ) +
  theme_minimal()

#-------------------------------------------------------------------------------
#Finding which shift has the most reported crimes.

shifts <- df %>%
  group_by(SHIFT) %>%
  summarise(count = n())

ggplot(shifts, aes(x = SHIFT, y = count, fill = SHIFT)) +
  geom_col() +
  geom_text(aes(label = count), vjust = 1.5, size = 4) +
  labs(title = 'Reported Incidence Per Shift', x = 'Shift', 
       y = 'Count of Incidence') + 
  theme_minimal()

#-------------------------------------------------------------------------------
#Finding top 4 offenses using faceted maps.

top_offenses4 <- df_clean %>%
  count(OFFENSE, sort = TRUE) %>%
  slice_max(n, n = 4) %>%
  pull(OFFENSE)

ggmap(dc_map) +
  geom_point(data = df_top, aes(x = LONGITUDE, y = LATITUDE),
             color = "red", alpha = 0.4, size = 0.8) +
  facet_wrap(~ OFFENSE, ncol = 2) +
  labs(
    title = "Top 4 Crime Types in Washington D.C. (Individual Incidents)",
    x = "Longitude", y = "Latitude"
  ) +
  theme_minimal() +
  theme(
    strip.text = element_text(face = "bold", size = 10),
    plot.title = element_text(hjust = 0.5, face = "bold", size = 14)
  )





