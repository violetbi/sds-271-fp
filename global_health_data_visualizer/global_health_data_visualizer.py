#!/usr/bin/env python
# coding: utf-8

# # SDS 271 Final Project 
# Group 1 Christy Yang, Vicky Xu, Xinran Bi, Yuzhang Fu
# ### Intro

# In[1]:


#import libraries needed
import pandas as pd
import json
import branca.colormap
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
import ipywidgets as widgets
from IPython.display import display
from ipyleaflet import Map, Choropleth, LegendControl
import geopandas as gpd
import branca.colormap
from ipywidgets import interactive_output
from mpl_toolkits.mplot3d import Axes3D


# In[ ]:


class DataVisualizer:    
    def __init__(self, csv_file):
        
        self.data = pd.read_csv(csv_file)
        self.regions = {
            "AFR": ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Comoros", "Ivory Coast", "Democratic Republic of the Congo", "Equatorial Guinea", "Eritrea", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Mozambique", "Namibia", "Niger", "Nigeria", "Republic of the Congo", "Rwanda", "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone", "South Africa", "South Sudan", "Eswatini", "Togo", "Uganda", "Tanzania", "Zambia", "Zimbabwe"],
            "AMR": ["Antigua and Barbuda", "Argentina", "Bahamas", "Barbados", "Belize", "Bolivia", "Brazil", "Canada", "Chile", "Colombia", "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "Ecuador", "El Salvador", "Grenada", "Guatemala", "Guyana", "Haiti", "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago", "United States", "Uruguay", "Venezuela"],
            "SEAR": ["Bangladesh", "Bhutan", "North Korea", "India", "Indonesia", "Maldives", "Myanmar", "Nepal", "Sri Lanka", "Thailand", "Timor-Leste"],
            "EUR": ["Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Israel", "Italy", "Kazakhstan", "Kyrgyzstan", "Latvia", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Tajikistan", "Turkey", "Turkmenistan", "Ukraine", "United Kingdom", "Uzbekistan"],
            "EMR": ["Afghanistan", "Bahrain", "Djibouti", "Egypt", "Iran", "Iraq", "Palestine", "Jordan", "Kuwait", "Lebanon", "Libya", "Morocco", "Oman", "Pakistan", "Qatar", "Saudi Arabia", "Somalia", "Sudan", "Syria", "Tunisia", "United Arab Emirates", "Yemen"],
            "WPR": ["Australia", "Brunei", "Cambodia", "China", "Cook Islands", "Fiji", "Japan", "Kiribati", "Laos", "Malaysia", "Marshall Islands", "Micronesia", "Mongolia", "Nauru", "New Zealand", "Niue", "Palau", "Papua New Guinea", "Philippines", "Samoa", "Singapore", "Solomon Islands", "South Korea", "Taiwan", "Tonga", "Tuvalu", "Vanuatu", "Vietnam"]
        }
        
        self.result_df = None  # Initialize result_df attribute #result of aggregation by region, TODO: rename it
        
#       self.data = self.load_data(file_path)
    
#     @staticmethod
#     def load_data(self, file_path):
#         """loads data from the given file path"""
#         data = pd.read_csv(file_path)
#         return data

    @staticmethod
    def check_same_entries_in_Indicator(self):
        """checks whether all entries in the 'Indicator' column are identical"""
        return self.data['Indicator'].nunique() == 1

    @staticmethod
    def plot_first_tooltip_by_location(self, period, column_name=None, location=None):
        """
        Plot the value of "First Tooltip" for Dim1 = 'Total' at a designated period for different locations.
        In particular, if column_name is not provided and all entries in the 'Indicator' column are identical,
        it uses the first entry in the 'Indicator' column as the column name.
        If the 'Dim1' column includes categories 'Urban', 'Total', and 'Rural', the function proceeds with plotting;
        otherwise, it notifies that the 'Dim1' column does not meet the specified criteria.
        """
        # Determine column name if not provided and all entries in 'Indicator' are identical
        if column_name is None and self.data['Indicator'].nunique() == 1:
            column_name = self.data['Indicator'].iloc[0]

        # Filter data for the specified period
        filtered_data = self.data[self.data['Period'] == period]

        # Filter data based on the specified location(s)
        if location is not None:
            if isinstance(location, str):
                location = [location]
            filtered_data = filtered_data[filtered_data['Location'].isin(location)]

        if 'Dim1' in self.data.columns and set(self.data['Dim1'].unique()) == {'Urban', 'Total', 'Rural'}:
            # Filter data for Dim1 categories 'Urban' and 'Rural'
            urban_rural_data = filtered_data[filtered_data['Dim1'].isin(['Urban', 'Rural'])]

            # Check if there's any data to plot
            if not urban_rural_data.empty:
                # Plotting for Urban and Rural categories side-by-side for each location
                unique_locations = urban_rural_data['Location'].unique()
                num_locations = len(unique_locations)

                fig, axes = plt.subplots(1, num_locations, figsize=(16, 6), sharey=True)
                fig.suptitle(f'{column_name} for Dim1 = Urban/Rural at Period {period}', fontsize=16)

                for i, loc in enumerate(unique_locations):
                    loc_data = urban_rural_data[urban_rural_data['Location'] == loc]
                    sns.barplot(x='Dim1', y='First Tooltip', data=loc_data, ax=axes[i])
                    axes[i].set_title(f'Location: {loc}', fontsize=14)
                    axes[i].set_xlabel('Dim1', fontsize=14)
                    axes[i].set_ylabel(column_name, fontsize=14)

                plt.tight_layout()
                plt.show()
            else:
                print("No data available for the specified combination.")
        else:
            print("Dim1 column does not meet the specified criteria.")
    
    @staticmethod
    def aggregate_data_by_region_and_year(self):
        # Create a DataFrame from the given data
        df = pd.DataFrame(self.data)

        df['Region'] = df['Location'].apply(lambda x: next((region for region, countries in self.regions.items() if x in countries), None))

        # Group by Region, Year, Dim1 and calculate the mean of 'First Tooltip'
        self.result_df = df.groupby(['Region', 'Indicator','Period', 'Dim1'])['First Tooltip'].mean().reset_index()

        return self.result_df
    
    
    @staticmethod
    def lineplot(self, location):
        if self.result_df is None:
            # If result_df is not yet computed, run the aggregation
            self.aggregate_data_by_region_and_year(self)

        is_region = location in self.regions.keys()

        if is_region:
            mask = self.result_df["Region"] == location
            data_location = self.result_df[mask]
            title_suffix = f" in {location} (Region)"
        else:
            mask = self.data["Location"] == location
            data_location = self.data[mask]
            title_suffix = f" in {location}"

        plt.figure(figsize=(12, 8))
        sns.lineplot(data=data_location, x='Period', y='First Tooltip', hue="Dim1")
        plt.title(f"Lineplot of {data_location['Indicator'].iloc[0]} over Time{title_suffix}")
        plt.xlabel("Time", fontsize=14)
        plt.ylabel(data_location['Indicator'].iloc[0], fontsize=14)
        plt.legend(title='Dimension', bbox_to_anchor=(1, 1), fontsize=14)
        plt.style.use('fivethirtyeight')
        plt.show()

    
    @staticmethod
    def scatterplot(self, location):
        mask = self.data["Location"] == location
        self.data_location = self.data[mask]
    
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=self.data_location, x='Period', y='First Tooltip', hue = "Dim1")
        plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.0f}"))
        plt.gca().yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.2f}"))
        plt.xlabel("Time", fontsize=14)
        plt.ylabel(f"{self.data.Indicator[0]}", fontsize=14)
        plt.legend(title='Dimension', bbox_to_anchor=(1, 1), fontsize=14)
        plt.title(f"{self.data.Indicator[0]} in {location} over Time")
        plt.style.use('fivethirtyeight')
        plt.show()

    # barplot
    @staticmethod
    def aggregate_years(data):
        aggregated_df = data.copy()
    
        # Aggregate years 2000-2005, 2006-2010, 2011-2017
        aggregated_df['Period'] = aggregated_df['Period'].astype(str) 
    
        aggregated_df.loc[aggregated_df['Period'].between('2000', '2005'), 'Period'] = '2000-2005'
        aggregated_df.loc[aggregated_df['Period'].between('2006', '2010'), 'Period'] = '2006-2010'
        aggregated_df.loc[aggregated_df['Period'].between('2011', '2017'), 'Period'] = '2011-2017'
    
        return aggregated_df
    
    @staticmethod
    def barplot(self, location):
        mask = self.data["Location"] == location
        df_location = self.data[mask]
        
        df_location_aggregated = self.aggregate_years(df_location)
#         df_location_aggregated = aggregate_years(df_location)
    
        # Define the desired order for the legend labels
        legend_order = ['2000-2005', '2006-2010', '2011-2017']
    
        plt.figure(figsize=(12, 8))
        sns.barplot(data=df_location_aggregated, x='Dim1', y='First Tooltip', hue='Period', hue_order=legend_order)
        plt.xlabel("Time", fontsize=14)
        plt.ylabel(f"{df_location_aggregated['Indicator'].iloc[0]}", fontsize=14)
        plt.legend(title='Year', bbox_to_anchor=(1, 1), fontsize=14)
        plt.title(f"{df_location_aggregated['Indicator'].iloc[0]} in {location} over Time")
        plt.style.use('fivethirtyeight')
        plt.show()
        
    @staticmethod
    def create_health_map_multilayer(self, initial_year):
        # Create a slider widget for the year
        year_slider = widgets.IntSlider(value=initial_year, min=self.data['Period'].min(), max=self.data['Period'].max(), description='Year')

        # Load a GeoDataFrame with country boundaries
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        # Create the initial map
        m = Map(center=(20, 0), zoom=2)
        display(m)

        # Initial empty Choropleth layer
        choro_layer = None  # Initialize with None

        def update_map(year):
            nonlocal choro_layer  # Use the outer variable

            # Filter for the specified year and dim1
            data_selected = self.data[(self.data['Period'] == year) & (self.data['Dim1'] == 'Total')]

            # Check if the filtered dataset is empty
            if data_selected.empty:
                # Print an error message
                print(f"No data available for the year {year} and dimension Total")
                return

            # Load a GeoDataFrame with country boundaries
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

            # Merge the dataset with the GeoDataFrame
            merged = world.set_index('name').join(data_selected.set_index('Location'))

            # Define the color scale
            color_scale = branca.colormap.linear.YlOrRd_09.scale(merged['First Tooltip'].min(), merged['First Tooltip'].max())

            # Create a Choropleth layer
            choro_layer = Choropleth(
                geo_data=merged.__geo_interface__,
                choro_data=dict(merged['First Tooltip']),
                colormap=color_scale,
                style={'fillOpacity': 0.8, 'dashArray': '5, 5'}
            )

            m.add_layer(choro_layer)

        # Set up an observer to update the map when the slider value changes
        output = interactive_output(update_map, {'year': year_slider})

        # Display the slider
        display(widgets.VBox([year_slider, output]))

    @staticmethod      
    def create_health_map(self, initial_year):
        # Create a slider widget for the year
        year_slider = widgets.IntSlider(value=initial_year, min=self.data['Period'].min(), max=self.data['Period'].max(), description='Year')

        # Load a GeoDataFrame with country boundaries
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        # Create the initial map
        m = Map(center=(20, 0), zoom=2)
        display(m)
        # Initial empty Choropleth layer
        choro_layer = None
        def update_map(year):
            nonlocal choro_layer  # Use the outer variable

            # Clear existing Choropleth layer if it exists
            if choro_layer:
                m.remove_layer(choro_layer)

            # Filter for the specified year and dim1
            data_selected = self.data[(self.data['Period'] == year) & (self.data['Dim1'] == 'Total')]

            # Check if the filtered dataset is empty
            if data_selected.empty:
                # Print an error message
                print(f"No data available for the year {year} and dimension Total")
                return

            # Load a GeoDataFrame with country boundaries
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

            # Merge the dataset with the GeoDataFrame
            merged = world.set_index('name').join(data_selected.set_index('Location'))

            # Define the color scale
            color_scale = branca.colormap.linear.YlOrRd_09.scale(merged['First Tooltip'].min(), merged['First Tooltip'].max())

            # Create a Choropleth layer
            choro_layer = Choropleth(
                geo_data=merged.__geo_interface__,
                choro_data=dict(merged['First Tooltip']),
                colormap=color_scale,
                style={'fillOpacity': 0.8, 'dashArray': '5, 5'}
            )

            m.add_layer(choro_layer)

        # Set up an observer to update the map when the slider value changes
        output = interactive_output(update_map, {'year': year_slider})

        # Display the slider
        display(widgets.VBox([year_slider, output]))


# In[ ]:




