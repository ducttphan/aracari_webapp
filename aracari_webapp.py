import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np
from pandas.core.reshape.concat import concat 
import streamlit as st 
import os

#Data Structures 
class DataGroup : 
    def __init__(self, name, timepoint, dataframe):
       self.name = name
       self.timepoint = timepoint
       self.dataframe = pd.DataFrame(data= dataframe)
    
    #Function to rename datatype parsing to dataframe (e.g. Tumor Area, Vascular Leak, etc.)
    def rename_dataframe(self, datatype, dataframe): 
        dataframe = self.dataframe
        dataframe = dataframe.rename(datatype)
        return dataframe

     #Function to calculate mean raw tumor area in pixel unit
    def calculateAvg(self, dataframe):
        dataframe = self.dataframe
        avg = dataframe.mean()
        return avg
    
    #Function to calculate standard deviation of tumor area in pixel unit
    def calculateSD(self, dataframe):
        dataframe = self.dataframe
        std = dataframe.std()
        return std

    #Function to calculate SEM of tumor area in pixel unit 
    def calculateSEM(self, dataframe):
        dataframe = self.dataframe
        sem = dataframe.sem()
        return sem

# Create a new class of DataGroup to store data
class DataSeries :

    #Initiate a Data object contains a name, timepoint, and a PANDAS series that takes  
    # raw tumor area from CellProfiler output .csv file 
    def __init__(self, name, timepoint, df):
        self.name = name 
        self.timepoint = timepoint
        self.df = pd.Series(data = df)
        self.df = self.df.rename('Value' + timepoint) 
    
    #Function to calculate mean raw tumor area in pixel unit
    def calculateAvg(self, df):
        df = self.df
        avg = df.mean()
        return avg
    
    #Function to calculate standard deviation of tumor area in pixel unit
    def calculateSD(self, df):
        df = self.df 
        std = df.std()
        return std

    #Function to calculate SEM of tumor area in pixel unit 
    def calculateSEM(self, df):
        df = self.df 
        sem = df.sem()
        return sem

#Main ReadMe
def ReadMe() : 
    st.markdown("""**Read Me:**  
    Aracari Biosciences provides a collection of web apps to assist with processing raw data 
    from different pipelines (e.g. CellProfiler, ImageJ/FIJI) into tabulated dataframes 
    for *post hoc* statistical analysis and data visualization. Select the type of analysis 
    and follow the instructions to process your data.   
    """)

#Tumor Growth Analysis  
def TumorGrowth() : 
    
    #ReadMe for Tumor Analysis App
    def TumorReadMe() : 
    
        st.markdown("""**Instructions:**  
        1. Type name of condition to be analyzed. (e.g. _Control_ or _Bevacizumab-100ng/mL_)  
        2. Indicate numbers of time points to be analyzed (e.g. 5 timepoint for 0h to 96h).  
        3. Type name of timepoint to be analyzed and upload its CellProfiler .csv file.   
        4. This app will automatically display a table summary of raw tumor area data and calculate __Mean/SD/SEM/N.__ In addition, it will also normalize raw data to T-0h and display __%Change/SD/SEM/N.__  
        5. Save your data tables to .csv files and export to your graphing app (e.g. Prism) or use Plot Data mode for quick data visualization.  
        6. Use your normalized summary .csv output files (i.e. condition_normalized summary.csv) in Plot Data mode.  """)

    #Extract raw data from CellProfiler pipeline and assemble into group according to conditions and timepoints
    def ExtractTumorData() : 
        datalist = []
        namelist = []
        savefile_key = 'savefile_'

        st.header('Extract Data')
        st.write("""__Instructions:__   
        1. Indicate number of groups in this dataset, according to your keylist.    
        2. List name of groups in this dataset according to your keylist, separated each by a comma (e.g. 100_PFU_mL, 300_PFU_mL).     
        3. Type in _name_ of the timepoint associated with this dataset (e.g. 0h, 24h, 48h). This will be used to label dataframe later.  
        4. Upload your dataset _*_Image.csv_ file from CellProfiler pipeline.   
        5. Type in directory path to save raw .csv files after sorting by groups. (e.g. _/Users/a/Desktop/data/_)  
        """)

        num_condition = st.text_input('Number of groups in this dataset, according to your keylist:')
        name_input = st.text_input('List name of groups in this dataset according to your keylist, separated each by a comma (e.g. 100_PFU_mL, 300_PFU_mL):')
        namelist = name_input.split(', ')

        timepoint_input = st.text_input("Timepoint associated with this dataset:")

        uploaded_file = st.file_uploader("Upload your CellProfiler *_Image.csv file:")
        uploaded_dataframe = pd.read_csv(uploaded_file, header= 0, index_col= 'Metadata_Key_Group')
        save_dir = st.text_input('Type directory to save raw data .csv files sorted by groups:')

        st.write('___')
        st.write("""## _Raw Data Sorted By Groups_  """)
        for i in range(0,int(num_condition)) :
            condition_dataframe = uploaded_dataframe.loc[namelist[i]]
            dataObj = DataGroup(namelist[i], timepoint_input, condition_dataframe)
            datalist.append(dataObj)

        st.write(datalist[i].dataframe)
        raw_csv = os.path.join(save_dir, namelist[i] + '_' + timepoint_input + '_raw_data.csv')
        saved = st.button('Save ' + namelist[i] + '_' + timepoint_input + '_raw_data.csv file', key= savefile_key + str(i))
        if saved:
            datalist[i].dataframe.to_csv(raw_csv)
            st.write('_Files saved_') 

    #Analyze tumor time course data
    def AnalyzeTumorData() :
        datapoint = []
        filenamelist = []

        #Collect condition name and number of timepoints
        with st.container() :
            group_name = st.sidebar.text_input('Name of condition:')
            datapoint_input = st.sidebar.text_input('Number of timepoint(s) in time course:') 

        st.header('Analyze Data')
        st.write("""__Instructions:__   
        1. Type in name your condition. (__Note:__ Avoid using special characters when naming. For example, replace "_10,000 RFU/mL_" with "_10K RFU(mL-1)_")    
        2. Indicate number of timepoint(s) in the time course experiment.  
        3. Type in _name_ of a timepoint (e.g. 0h, 24h, 48h). This will be used to label dataframe later.  
        4. Upload your _*_Image.csv_ file from CellProfiler pipeline for each time point.   
        5. Type in directory path to save raw or normalized .csv files. (e.g. _/Users/a/Desktop/data/_)  
        """)
        #Define keys to keep track on timepoints and files uploaded
        t = 't_'
        u = 'upload_'

        #Read and parse tumor area raw data into individual DataGroup objects 
        for i in range(0,int(datapoint_input)) :
            time_point = st.text_input('Timepoint of dataset:', key= t + str(i))  
            uploaded_file = st.file_uploader("Select .csv file:", key= u + str(i)) 
            raw_data = pd.read_csv(uploaded_file)

            raw_TumorArea = raw_data['AreaOccupied_AreaOccupied_Identify_Tumor']
            file_name = raw_data['FileName_Orig_Tumor']
            dataObj = DataSeries(group_name, time_point, raw_TumorArea)
            datapoint.append(dataObj)
            filenamelist.append(file_name)

        st.write('___  ')
        #Display raw data table. Calculate mean, SD, SEM of tumor area of each timepoint    
        avg_dataObj = []
        std_dataObj = []
        sem_dataObj = []
        group_id = []
        n_row = []

        raw_df = pd.DataFrame(data= None)

        for i in range(0, int(datapoint_input)) :
            avg_dataObj.append(datapoint[i].calculateAvg(raw_TumorArea))
            std_dataObj.append(datapoint[i].calculateSD(raw_TumorArea))
            sem_dataObj.append(datapoint[i].calculateSEM(raw_TumorArea))   
            group_id.append(datapoint[i].name + '_' + datapoint[i].timepoint)
            n_row.append(datapoint[i].df.size)
            raw_df.insert(loc=i, column= group_id[i], value= datapoint[i].df) #Construct raw tumor area dataframe 
            tabulated_df = raw_df.join(filenamelist[i]) #Join filenames to its corresponnding data

        st.write("""### __Raw Data__ """)
        st.write(tabulated_df)
        st.write("""### __Mean, SD, SEM__ """)

        #Tabulate mean, SD, SEM of all datapoints into new dataframe
        df_summary = pd.DataFrame(data = [avg_dataObj, std_dataObj, sem_dataObj, n_row], index = ['Mean','SD','SEM', 'N'], columns= group_id)
        st.write(df_summary)

        with st.form('save_raw pixel_files') :
                save_dir = st.text_input('Type directory to save raw dataframe and Mean/SD/SEM .csv files:')
                tabulated_df_csv = os.path.join(save_dir, group_name + '_raw_dataframe.csv')
                raw_summary_csv = os.path.join(save_dir, group_name + '_raw_summary.csv')
                saved = st.form_submit_button('Save')
                if saved:
                    tabulated_df.to_csv(tabulated_df_csv)
                    df_summary.to_csv(raw_summary_csv)
                    st.write('_Files saved_')


        st.write('___  ')

        #Normalize raw data to T-0h
        normalized_df = pd.DataFrame(data=None)
        avg_percent_change = []
        normalized_std = []
        normalized_sem = []
        normalized_n_row = []

        for i in range(0, int(datapoint_input)) :
            normalized_df.insert(loc= i, column= group_id[i], value= raw_df[group_id[i]]/raw_df[group_id[0]])
            tabulated_normalized_df = normalized_df.join(filenamelist[i])
            normalized_n_row.append(normalized_df[group_id[i]].size)
            avg_percent_change.append(normalized_df[group_id[i]].mean())
            normalized_std.append(normalized_df[group_id[i]].std())
            normalized_sem.append(normalized_df[group_id[i]].sem())


        st.write("""### __Normalized Data__ """)
        st.write(tabulated_normalized_df)
        st.write("""### __%Change, SD, SEM__ """)

        normalized_summary = pd.DataFrame(data = [avg_percent_change, normalized_std, normalized_sem, normalized_n_row], index = ['%Change','SD','SEM', 'N'], columns= group_id)
        st.write(normalized_summary)

        with st.form('save_normalized_files') :
            save_dir = st.text_input('Type directory to save normalized dataframe and %Change/SD/SEM .csv files:')
            tabulated_normalized_df_csv = os.path.join(save_dir, group_name + '_normalized_dataframe.csv')
            normalized_summary_csv = os.path.join(save_dir, group_name + '_normalized_summary.csv')
            saved = st.form_submit_button('Save')
            if saved:
                tabulated_normalized_df.to_csv(tabulated_normalized_df_csv)
                normalized_summary.to_csv(normalized_summary_csv)
                st.write('_Files saved_')

    #Run statistical analysis and plot tumor growth data
    def PlotTumorData() :

        condition_key = 'condition_'
        file_key = 'file_key_'

        name_list = []
        data_list = []
        sd_list = []
        sem_err_list = []

        st.header('Plot Data')
        st.write("""__Instructions:__   
        1. Name your condition as how you want it to display on the plot (e.g. Drug "A" - 1 mg/mL).  
        2. Upload your __<condition>_normalized_summary.csv__ files from Analyze Data mode.   
        3. Use sidebar options to customize your plot.  
        """)
        st.write('___  ')
        plot_title = st.sidebar.text_input('Type in plot title:')
        x_axis_input = st.sidebar.text_input('Type in timepoint(s), separated by a comma (e.g. "T-0h, T-24h"):')
        
        
        
        x_axis = x_axis_input.split(', ')

        st.write("""## _Plot Setup_  """)

        n_condition = st.text_input('Number of condition(s) to plot:')
        for i in range(0, int(n_condition)) : 
            condition_name = st.text_input("Name of condition:", key= condition_key + str(i))
            condition_file = st.file_uploader('Select file to upload', key= file_key + str(i))
            condition_data = pd.read_csv(condition_file, header=0, index_col=0)

            per_change = condition_data.iloc[0]
            sd = condition_data.iloc[1]
            sem = condition_data.iloc[2]
            plot_data_series = pd.Series(data= per_change)
            plot_sd_series = pd.Series(data= sd)
            plot_sem_series = pd.Series(data= sem)
            
            name_list.append(condition_name)
            data_list.append(plot_data_series)
            sd_list.append(plot_sd_series)
            sem_err_list.append(plot_sem_series)
        
        st.write('___  ')
        st.write("""## _Auto-Generated Plot_  """)

        fig = plt.figure(figsize= [6.0, 4.0])
        for i in range(0, int(n_condition)) :
            plt.errorbar(x= x_axis, y= data_list[i], yerr= sem_err_list[i], label= name_list[i], marker = 'o', capsize= 3)
        
        #Select plot theme
        theme_options = ['default', 'seaborn', 'ggplot', 'seaborn-white', 'seaborn-deep', 'grayscale']
        theme_selection = st.sidebar.selectbox('Select plot theme:', theme_options, index= 0)
        plt.style.use(theme_selection)

        #Scale y-axis 
        y_axis_lim = st.sidebar.slider('Select y-axis limit:',min_value= 0, max_value= 10, value= (0, 4))
        plt.ylim(y_axis_lim)

        #Label plot
        plt.title(plot_title)
        plt.grid(color = 'black', linestyle = 'dotted', linewidth = 0.2)
        plt.xlabel('Time point')
        plt.ylabel('% Change')
        plt.legend(loc= 'best')

        st.write(fig)
        st.write('_Error bars = SEM_  ')
        
    modeOptions = ['Instructions', 'Extract Data', 'Analyze Data', 'Plot Data']

    st.title('TUMOR GROWTH ANALYSIS')
    st.write("This app will extract tumor area measurements from CellProfiler .csv files and perform tumor growth analysis.  ")

    st.header('Select Mode:')
    mode = st.radio("", modeOptions, index=0)
    tabMethods = [TumorReadMe, ExtractTumorData, AnalyzeTumorData, PlotTumorData]
    tabMethods[modeOptions.index(mode)]()  

#Vessel Morphometry Analysis 
def VesselMorphometry() :
    
    st.title('VESSEL MORPHOMETRY ANALYSIS')
    st.write("This app will extract vessel morphometry measurements (e.g. Vessels Area, Total Vessel Length, Branchpoints, Lacunarity) from AngioTool .xls files and tabulate according to conditions.  ")

    angiotool_header = ['Image_Name', 'Date', 'Time', 'File_Location', 'Low_Threshold', 'High_Threshold', 
    'Vessel_Thickness', 'Small_Particles', 'Fill_Holes', 'Scaling_Factor', 'NA', 'Explant_Area', 
    'Vessels_Area', 'Vessels_Percentage_Area', 'Total_Branchpoints', 'Junctions_Density', 'Total_Vessels_Length', 
    'Average_Vessels_Length', 'Total_Endpoints', 'Average_Lacunarity']

    keylist_header = ['Group', 'File_Location', 'Image_Name']

    st.header('Processing AngioTool Output File')
    st.markdown("""**Instructions:**  
    1. Upload AngioTool combined_report.xls file.  
    2. Upload a keylist .csv file that can be used to sort data by group.  
    3. Information from the keylist (e.g., Group, File_Location) will be appended 
    to the raw dataframe for sorting purpose.       
    """)

    st.markdown("""
    Key List Template:
    
    | Group   | File_Location             | Image_Name                |
    |---------|:-------------------------:|--------------------------:|
    | Control | /data/P1_D1_0001_DAPI.jpg | P1_D1_0001_DAPI.jpg       |
    | Test    | /data/P1_D1_0002_DAPI.jpg | P1_D1_0002_DAPI.jpg       |     
    
    """)
    st.write('____  ')

    uploaded_angiotool_file = st.file_uploader("Upload your Angiotool .xls report file:")
    uploaded_xls = pd.read_excel(uploaded_angiotool_file, header= 3, names= angiotool_header) 

    uploaded_keylist_file = st.file_uploader("Upload your keylist .csv file to sort data by group:")
    uploaded_keylist_csv = pd.read_csv(uploaded_keylist_file, header= 0, names= keylist_header)

    image_name = pd.DataFrame(uploaded_xls['Image_Name'])
    vessels_area = pd.DataFrame(uploaded_xls['Vessels_Area'])
    vessels_length = pd.DataFrame(uploaded_xls['Total_Vessels_Length'])
    branchpoints = pd.DataFrame(uploaded_xls['Total_Branchpoints'])
    lacunarity = pd.DataFrame(uploaded_xls['Average_Lacunarity'])
    angiotool_df = pd.concat([image_name, vessels_area, vessels_length, branchpoints, lacunarity], axis= 1)
    df = pd.merge(uploaded_keylist_csv, angiotool_df, on= ['Image_Name'])

    st.write("""### _Raw Data_  """)
    st.write(df)
    st.write('___')

    st.header('Sorting Data')
    st.markdown("""**Instructions:**  
        1. Type in name of group to extract data.  
        2. Vessel morphometry data in pixel units (vessel area, total vessel length, number of branchpoints, lacunarity) 
        belong to this group will be sorted and tabulated into a new dataframe.  
        3. Statistical summary (Mean, SD, SEM, N) will be generated based on the tabulated dataframe.  
        4. Type in directory path to save .csv files. (e.g. _/Users/a/Desktop/data/_).       
        """)
    group_name = st.text_input('Name of group to extract data:')
    group_rawdata = df[df["Group"] == group_name]
    n_row = len(group_rawdata.index)

    mean_vessels_area = group_rawdata['Vessels_Area'].mean()
    std_vessels_area = group_rawdata['Vessels_Area'].std()
    sem_vessels_area = group_rawdata['Vessels_Area'].sem()
    group_vessels_area_summary = pd.Series([mean_vessels_area, std_vessels_area, sem_vessels_area, n_row], 
        index= ['Mean', 'SD', 'SEM', 'N'], name= 'Vessels_Area')

    mean_vessels_length = group_rawdata['Total_Vessels_Length'].mean()
    std_vessels_length = group_rawdata['Total_Vessels_Length'].std()
    sem_vessels_length = group_rawdata['Total_Vessels_Length'].sem()
    group_vessels_length_summary = pd.Series([mean_vessels_length, std_vessels_length, sem_vessels_length, n_row], 
        index= ['Mean', 'SD', 'SEM', 'N'], name= 'Vessels_Length')

    mean_branchpoints = group_rawdata['Total_Branchpoints'].mean()
    std_branchpoints = group_rawdata['Total_Branchpoints'].std()
    sem_branchpoints = group_rawdata['Total_Branchpoints'].sem()
    group_branchpoints_summary = pd.Series([mean_branchpoints, std_branchpoints, sem_branchpoints, n_row], 
        index= ['Mean', 'SD', 'SEM', 'N'], name= 'Vessel_Branchpoints')

    mean_lacunarity = group_rawdata['Average_Lacunarity'].mean()
    std_lacunarity = group_rawdata['Average_Lacunarity'].std()
    sem_lacunarity = group_rawdata['Average_Lacunarity'].sem()
    group_lacunarity_summary = pd.Series([mean_lacunarity, std_lacunarity, sem_lacunarity, n_row], 
        index= ['Mean', 'SD', 'SEM', 'N'], name= 'Average_Lacunarity')

    group_summary = pd.concat([group_vessels_area_summary, group_vessels_length_summary, 
        group_branchpoints_summary, group_lacunarity_summary], axis= 1)

    st.write("""### _Tabulated Data_  """)
    st.write(group_rawdata)
    st.write("""### _Data Summary_  """)
    st.write(group_summary)

    with st.form('save_csv_files') :
        save_dir = st.text_input('Type directory to save tabulated dataframe and summary .csv files:')
        group_df_csv = os.path.join(save_dir, group_name + '_tabulated_dataframe.csv')
        group_summary_csv = os.path.join(save_dir, group_name + '_data_summary.csv')
        saved = st.form_submit_button('Save')
        if saved:
            group_rawdata.to_csv(group_df_csv)
            group_summary.to_csv(group_summary_csv)
            st.write('_Files saved_')

#Permeability Analysis
def VesselPermeability() : 
    def PermeabilityReadMe() : 
    
        st.markdown("""**Instructions:**  
        1. Type name of condition to be analyzed. (e.g. _Control_ or _Bevacizumab-100ng/mL_)  
        2. This app will automatically display a table summary of raw permeability data and calculate __Mean/SD/SEM/N.__   
        4. Save your data tables to .csv files and export to your graphing app (e.g. Prism) or use Plot Data mode for quick data visualization.  
        5. Use your permeability_summary.csv output files (i.e. condition_permeability_summary.csv) in Plot Data mode.  """)

    def TabulatePermeabilityData() : 

        st.header('Tabulate Data')
        st.write("""__Instructions:__   
        1. Type in name of your group. (__Note:__ Avoid using special characters when naming. For example, replace "_10,000 RFU/mL_" with "_10K RFU(mL-1)_")   
        2. Upload __ALL__ raw .csv files that belong to this group.   
        3. Type in directory path to save .csv files. (e.g. _/Users/a/Desktop/data/_).  
        """)

        filelist = []
        average_ROI = []
        name_input = st.text_input("Name of group:")
        uploaded_files = st.file_uploader("Select all .csv files belong to this group:", accept_multiple_files= True)

        uploaded_file_count = len(uploaded_files)

        for file in uploaded_files: 
            file_csv = pd.read_csv(file)
            filelist.append(file.name)
            average_ROI.append(file_csv.mean())
            df = pd.DataFrame(data= average_ROI, index= filelist)

        avg_leak = df['Vascular Leak'].mean() 
        std_leak = df['Vascular Leak'].std()
        sem_leak = df['Vascular Leak'].sem()
        num_row = len(df)
        summary = pd.Series(data=[avg_leak, std_leak, sem_leak, num_row], index= ['Avg. Vasc. Leak', 'SD', 'SEM', 'N'], name= name_input)

        st.write(df)
        st.write(summary)
        with st.form('save_raw pixel_files') :
                    save_dir = st.text_input('Type directory to save dataframe and summary .csv files:')
                    df_csv = os.path.join(save_dir, name_input + '_permeability_dataframe.csv')
                    summary_csv = os.path.join(save_dir, name_input + '_permeability_summary.csv')
                    saved = st.form_submit_button('Save')
                    if saved:
                        df.to_csv(df_csv)
                        summary.to_csv(summary_csv)
                        st.write('_Files saved_')


    #Run statistical analysis and plot data
    def PlotPermeabilityData() :

        condition_key = 'condition_'
        file_key = 'file_key_'

        name_list = []
        data_list = []
        sd_list = []
        sem_err_list = []

        st.header('Plot Data')
        st.write("""__Instructions:__   
        1. Name your condition as how you want it to display on the plot (e.g. Drug "A" - 1 mg/mL).  
        2. Upload your __<condition>_permeability_summary.csv__ files from Tabulate Data mode.   
        3. Use sidebar options to customize your plot.  
        """)
        st.write('___  ')
        plot_title = st.sidebar.text_input('Type in plot title:')

        st.write("""## _Plot Setup_  """)

        n_condition = st.text_input('Number of condition(s) to plot:')
        for i in range(0, int(n_condition)) : 
            condition_name = st.text_input("Name of condition:", key= condition_key + str(i))
            condition_file = st.file_uploader('Select file to upload', key= file_key + str(i))
            condition_data = pd.read_csv(condition_file, header=0, index_col=0)

            avg_leak = condition_data.iloc[0]
            sd = condition_data.iloc[1]
            sem = condition_data.iloc[2]
            
            name_list.append(condition_name)
            data_list.append(avg_leak)
            sd_list.append(sd)
            sem_err_list.append(sem)
        
        st.write('___  ')
        st.write("""## _Auto-Generated Plot_  """)

        fig = plt.figure(figsize= [6.0, 4.0])
        for i in range(0, int(n_condition)) :
            plt.bar(x= name_list[i], height= data_list[i], yerr= sem_err_list[i], capsize= 2)
        
        #Select plot theme
        theme_options = ['default', 'seaborn', 'ggplot', 'seaborn-white', 'seaborn-deep', 'grayscale']
        theme_selection = st.sidebar.selectbox('Select plot theme:', theme_options, index= 0)
        plt.style.use(theme_selection)

        #Label plot
        plt.title(plot_title)
        plt.grid(color = 'black', linestyle = 'dotted', linewidth = 0.2)
        plt.xlabel('Condition')
        plt.ylabel('Vascular Leak (RFU)')

        st.write(fig)
        st.write('_Error bars = SEM_  ')

    modeOptions = ['Instructions', 'Tabulate Data', 'Plot Data']

    st.title('VESSEL PERMEABILITY ANALYSIS')
    st.write("This app will tabulate vessel leak measurements from ImageJ/FIJI .csv files and perform permeability analysis.  ")

    st.header('Select Mode:')
    mode = st.radio("", modeOptions, index=0)
    tabMethods = [PermeabilityReadMe, TabulatePermeabilityData, PlotPermeabilityData]
    tabMethods[modeOptions.index(mode)]()  

#PBMC Infiltration Analysis 
def PBMCInfiltration() : 
    
    #ReadMe function 
    def ReadMe() : 
    
        st.markdown("""**Instructions:**  
        1. __Extract Data__ will take a raw PBMC count .csv file from CellProfiler and extract data according to different groups based on a metadata keylist.    
        2. __Analyze Data__ will tabulate adhered/extravasated/total PBMC counts from .csv file (from Extract Data pipeline or pre-sorted in CellProfiler).  
        3. __Plot Data__ will take tabulated adhered/extravasated PBMC data and generate a stack bar graph with SEM.  """)

    def ExtractPBMCData() :
        datalist = []
        namelist = []
        savefile_key = 'savefile_'

        st.markdown("""**Instructions:**  
        1. Type in the number of group in this dataset according to the metadata keylist.    
        2. Type in the name of groups in this dataset according to the metadata keylist.  
        3. Type in the time point associated with this dataset.  """)


        num_condition = st.text_input('Number of groups in this dataset, according to your keylist:')
        name_input = st.text_input('List name of groups in this dataset according to your keylist, separated each by a comma (e.g. TNFa_100_ng_mL, TNFa_300_ng_mL):')
        namelist = name_input.split(', ')
        timepoint_input = st.text_input("Time point associated with this dataset:")

        uploaded_file = st.file_uploader("Upload your CellProfiler *_Image.csv file:")
        uploaded_dataframe = pd.read_csv(uploaded_file, header= 0, index_col= 'Metadata_Key_Group')
        save_dir = st.text_input('Type directory to save raw data .csv files sorted by groups:')

        st.write('___')
        st.write("""## _Raw Data Sorted By Groups_  """)
        for i in range(0, int(num_condition)) :
            condition_dataframe = uploaded_dataframe.loc[namelist[i]]
            dataObj = DataGroup(namelist[i], timepoint_input, condition_dataframe)
            datalist.append(dataObj)

            st.write(datalist[i].dataframe)
            raw_csv = os.path.join(save_dir, namelist[i] + '_' + timepoint_input + '_raw_data.csv')
            saved = st.button('Save ' + namelist[i] + '_' + timepoint_input + '_raw_data.csv file', key= savefile_key + str(i))
            if saved:
                datalist[i].dataframe.to_csv(raw_csv)
                st.write('_Files saved_') 

    def AnalyzePBMCData() : 

        st.header('Analyze Data')
        st.write("""__Instructions:__   
        1. Name your condition and the timepoint associated with it. (e.g. Control_2h).  
        2. Upload your __<condition>_<timepoint>_raw_data.csv__ files from Extract Data mode.  
        3. If you have separated and analyzed data according to conditions directly in CellProfiler, upload your *_Image.csv file.  
        """)

        condition_name = st.text_input('Name of condition:')
        uploaded_file = st.file_uploader("Select .csv file:") 
        raw_csv = pd.read_csv(uploaded_file)


        total_PBMC = raw_csv['Count_TotalPBMC']
        n_totalPBMC = len(total_PBMC.index)

        extravasated_PBMC = raw_csv['Count_ExtravasatedPBMC']
        n_extravasatedPBMC = len(extravasated_PBMC.index)

        n_adheredPBMC = n_totalPBMC

        mean_totalPBMC = raw_csv['Count_TotalPBMC'].mean()
        mean_extravasatedPBMC = raw_csv['Count_ExtravasatedPBMC'].mean()
        mean_adheredPBMC = mean_totalPBMC - mean_extravasatedPBMC 

        std_totalPBMC = raw_csv['Count_TotalPBMC'].std()
        std_extravasatedPBMC = raw_csv['Count_ExtravasatedPBMC'].std()
        std_adheredPBMC = std_totalPBMC - std_extravasatedPBMC 

        sem_totalPBMC = raw_csv['Count_TotalPBMC'].sem()
        sem_extravasatedPBMC = raw_csv['Count_ExtravasatedPBMC'].sem()
        sem_adheredPBMC = sem_totalPBMC - sem_extravasatedPBMC 

        mean_df = pd.Series([mean_adheredPBMC, mean_extravasatedPBMC, mean_totalPBMC], index= [condition_name + '_' + 'Adhered_PBMC', condition_name + '_' + 'Extravasated_PBMC', condition_name + '_' + 'Total_PBMC'])
        std_df = pd.Series([std_adheredPBMC, std_extravasatedPBMC, std_totalPBMC], index= [condition_name + '_' + 'Adhered_PBMC', condition_name + '_' + 'Extravasated_PBMC', condition_name + '_' + 'Total_PBMC'])
        sem_df = pd.Series([sem_adheredPBMC, sem_extravasatedPBMC, sem_totalPBMC], index= [condition_name + '_' + 'Adhered_PBMC', condition_name + '_' + 'Extravasated_PBMC', condition_name + '_' + 'Total_PBMC'])
        nrow_df = pd.Series([n_adheredPBMC, n_extravasatedPBMC, n_totalPBMC], index= [condition_name + '_' + 'Adhered_PBMC', condition_name + '_' + 'Extravasated_PBMC', condition_name + '_' + 'Total_PBMC'])

        raw_df = pd.DataFrame([mean_df, std_df, sem_df, nrow_df], index= ['Mean', 'SD', 'SEM', 'N'])

        st.write(raw_df)

        with st.form('save_rawdf') :
            save_dir = st.text_input('Type directory to save the PBMC infiltration summary .csv file:')
            raw_summary_csv = os.path.join(save_dir, condition_name + '_PBMC_infiltration_summary.csv')
            saved = st.form_submit_button('Save')
            if saved:
                raw_df.to_csv(raw_summary_csv)
                st.write('_Files saved_')

    def PlotPBMCData() : 

        condition_key = 'condition_'
        file_key = 'file_key_'

        totalPBMC_list = []
        totalPBMC_std_list = []
        totalPBMC_sem_list = []

        extravasatedPBMC_list = []
        extravasatedPBMC_std_list = []
        extravasatedPBMC_sem_list = []

        adheredPBMC_list = []
        adheredPBMC_std_list = []
        adheredPBMC_sem_list = []

        st.header('Plot Data')
        st.write("""__Instructions:__   
        1. Name your plot title (e.g. Drug "A" - 1 mg/mL - 2h).  
        2. Upload your __<condition>_PBMC_infiltration_summary.csv__ file from Analyze Data mode.   
        3. Use sidebar options to customize your plot.  
        """)
        st.write('___  ')
        plot_title = st.sidebar.text_input('Type in plot title:')
        n_timepoint = st.sidebar.text_input('Number of time points to plot:')
        x_axis_input = st.sidebar.text_input('Type in timepoint labels, separated by a comma (e.g. "T-2h, T-6h, T-12h"):')
        x_axis = x_axis_input.split(', ')

        #Select plot theme
        theme_options = ['default', 'seaborn', 'ggplot', 'seaborn-white', 'seaborn-deep', 'grayscale']
        theme_selection = st.sidebar.selectbox('Select plot theme:', theme_options, index= 0)
        plt.style.use(theme_selection)

        for i in range(0, int(n_timepoint)) :
            timepoint_name = st.text_input("Timepoint:", key= condition_key + str(i))
            timepoint_file = st.file_uploader('Select file to upload:', key= file_key + str(i))
            timepoint_data = pd.read_csv(timepoint_file, header=0, index_col=0)

            mean_totalPBMC = timepoint_data.iloc[0,2]
            std_totalPBMC = timepoint_data.iloc[1,2]
            sem_totalPBMC = timepoint_data.iloc[2,2]

            mean_extravasatedPBMC = timepoint_data.iloc[0,1]
            std_extravasatedPBMC = timepoint_data.iloc[1,1]
            sem_extravasatedPBMC = timepoint_data.iloc[2,1]

            mean_adheredPBMC = timepoint_data.iloc[0,0]
            std_adheredPBMC = timepoint_data.iloc[1,0]
            sem_adheredPBMC = timepoint_data.iloc[2,0]

            totalPBMC_list.append(mean_totalPBMC)
            totalPBMC_std_list.append(std_totalPBMC)
            totalPBMC_sem_list.append(sem_totalPBMC)

            extravasatedPBMC_list.append(mean_extravasatedPBMC)
            extravasatedPBMC_std_list.append(std_extravasatedPBMC)
            extravasatedPBMC_sem_list.append(sem_extravasatedPBMC)

            adheredPBMC_list.append(mean_adheredPBMC)
            adheredPBMC_std_list.append(std_adheredPBMC)
            adheredPBMC_sem_list.append(sem_adheredPBMC)

        st.write('___  ')
        st.write("""## _Auto-Generated Plot_  """)

        fig = plt.figure(figsize= [6.0, 4.0])
        
        plt.bar(x= x_axis, height= adheredPBMC_list, yerr= adheredPBMC_sem_list, label= 'Adhered PBMC', capsize = 3)
        plt.bar(x= x_axis, height= extravasatedPBMC_list, yerr= extravasatedPBMC_sem_list, label= 'Extravasated PBMC', bottom= adheredPBMC_list, capsize = 3)
        
        plt.title(plot_title)
        plt.grid(color = 'black', linestyle = 'dotted', axis= 'y', linewidth = 0.2)
        plt.xlabel('Time Point')
        plt.ylabel('PBMC Counts')
        plt.legend()
        st.write(fig)

    #Main function 
    modeOptions = ['Read Me', 'Extract Data', 'Analyze Data', 'Plot Data']

    st.title('PBMC INFILTRATION ANALYSIS')
    st.write("This app will extract PBMC counts from CellProfiler .csv files and perform PBMC infiltration analysis.  ")

    st.header('Select Mode:')
    mode = st.radio("", modeOptions, index=0)
    tabMethods = [ReadMe, ExtractPBMCData, AnalyzePBMCData, PlotPBMCData]
    tabMethods[modeOptions.index(mode)]()   

#Main function 
main_modeOptions = ['ReadMe', 'Tumor Growth Analysis', 'Vessel Morphometry Analysis', 'Vessel Permeability Analysis', 'PBMC Infiltration Analysis']

st.image(image='Linear_Logo.tif')
st.write('  ')
st.header('Select Type of Analysis:')
mode = st.radio("", main_modeOptions, index=0)
st.write('---')
tabMethods = [ReadMe, TumorGrowth, VesselMorphometry, VesselPermeability, PBMCInfiltration]
tabMethods[main_modeOptions.index(mode)]()   
