import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Data Science Salary Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('ds_salaries.csv')
    
    # Data transformations
    exp_level_map = {
        'EN': 'Entry-level',
        'MI': 'Mid-level',
        'SE': 'Senior-level',
        'EX': 'Executive-level'
    }
    df['experience_level'] = df['experience_level'].map(exp_level_map)
    
    emp_type_map = {
        'FT': 'Full-time',
        'PT': 'Part-time',
        'CT': 'Contract',
        'FL': 'Freelance'
    }
    df['employment_type'] = df['employment_type'].map(emp_type_map)
    
    company_size_map = {
        'S': 'Small',
        'M': 'Medium',
        'L': 'Large'
    }
    df['company_size'] = df['company_size'].map(company_size_map)
    
    df['remote_work_type'] = pd.cut(df['remote_ratio'],
                                   bins=[-1, 0, 50, 100],
                                   labels=['On-site', 'Hybrid', 'Full-remote'])
    
    def get_region(country_code):
        americas = ['US', 'CA', 'MX', 'BR', 'CO']
        europe = ['GB', 'DE', 'ES', 'FR', 'NL', 'PT', 'CH', 'IE', 'AT', 'SI', 'HR']
        asia = ['IN', 'SG', 'JP', 'HK', 'IL', 'AE', 'PK', 'TH']
        oceania = ['AU', 'NZ']
        africa = ['NG', 'KE', 'GH']
        
        if country_code in americas:
            return 'Americas'
        elif country_code in europe:
            return 'Europe'
        elif country_code in asia:
            return 'Asia'
        elif country_code in oceania:
            return 'Oceania'
        elif country_code in africa:
            return 'Africa'
        else:
            return 'Other'
    
    df['region'] = df['company_location'].apply(get_region)
    
    def categorize_job(title):
        title = title.lower()
        if 'data scientist' in title:
            return 'Data Scientist'
        elif 'data engineer' in title:
            return 'Data Engineer'
        elif 'data analyst' in title:
            return 'Data Analyst'
        elif 'machine learning' in title or 'ml' in title:
            return 'Machine Learning Engineer'
        elif 'research' in title or 'scientist' in title:
            return 'Research Scientist'
        elif 'analytics' in title:
            return 'Analytics Engineer'
        elif 'architect' in title:
            return 'Data Architect'
        elif 'manager' in title or 'lead' in title or 'director' in title or 'head' in title:
            return 'Management'
        else:
            return 'Other'
    
    df['job_category'] = df['job_title'].apply(categorize_job)
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.header('Filter Data')
selected_years = st.sidebar.multiselect(
    'Select Years',
    options=sorted(df['work_year'].unique()),
    default=sorted(df['work_year'].unique())
)

selected_exp_levels = st.sidebar.multiselect(
    'Select Experience Levels',
    options=df['experience_level'].unique(),
    default=df['experience_level'].unique()
)

selected_job_cats = st.sidebar.multiselect(
    'Select Job Categories',
    options=df['job_category'].unique(),
    default=df['job_category'].unique()
)

selected_regions = st.sidebar.multiselect(
    'Select Regions',
    options=df['region'].unique(),
    default=df['region'].unique()
)

selected_company_sizes = st.sidebar.multiselect(
    'Select Company Sizes',
    options=df['company_size'].unique(),
    default=df['company_size'].unique()
)

selected_remote_types = st.sidebar.multiselect(
    'Select Remote Work Types',
    options=df['remote_work_type'].unique(),
    default=df['remote_work_type'].unique()
)

# Apply filters
filtered_df = df[
    (df['work_year'].isin(selected_years)) &
    (df['experience_level'].isin(selected_exp_levels)) &
    (df['job_category'].isin(selected_job_cats)) &
    (df['region'].isin(selected_regions)) &
    (df['company_size'].isin(selected_company_sizes)) &
    (df['remote_work_type'].isin(selected_remote_types))
]

# Main dashboard
st.title('💰 Data Science Salary Dashboard')
st.markdown("""
This dashboard provides insights into data science salaries from around the world.
Use the filters in the sidebar to customize the view.
""")

# Key metrics
st.subheader('Key Metrics')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(filtered_df))
col2.metric("Average Salary (USD)", f"${filtered_df['salary_in_usd'].mean():,.0f}")
col3.metric("Median Salary (USD)", f"${filtered_df['salary_in_usd'].median():,.0f}")
col4.metric("Highest Salary (USD)", f"${filtered_df['salary_in_usd'].max():,.0f}")

# Salary distribution
st.subheader('Salary Distribution')
fig1 = px.histogram(filtered_df, x='salary_in_usd', nbins=50, 
                   title='Distribution of Salaries in USD',
                   labels={'salary_in_usd': 'Salary in USD'})
st.plotly_chart(fig1, use_container_width=True)

# Salary by experience level
st.subheader('Salary by Experience Level')
fig2 = px.box(filtered_df, x='experience_level', y='salary_in_usd',
             category_orders={'experience_level': ['Entry-level', 'Mid-level', 'Senior-level', 'Executive-level']},
             title='Salary Distribution by Experience Level',
             labels={'salary_in_usd': 'Salary in USD', 'experience_level': 'Experience Level'})
st.plotly_chart(fig2, use_container_width=True)

# Salary by region and job category
st.subheader('Salary by Region and Job Category')

tab1, tab2 = st.tabs(['Average Salary', 'Median Salary'])

with tab1:
    region_job_avg = filtered_df.groupby(['region', 'job_category'])['salary_in_usd'].mean().reset_index()
    fig3 = px.bar(region_job_avg, x='region', y='salary_in_usd', color='job_category',
                 title='Average Salary by Region and Job Category',
                 labels={'salary_in_usd': 'Average Salary in USD', 'region': 'Region', 'job_category': 'Job Category'},
                 barmode='group')
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    region_job_median = filtered_df.groupby(['region', 'job_category'])['salary_in_usd'].median().reset_index()
    fig4 = px.bar(region_job_median, x='region', y='salary_in_usd', color='job_category',
                 title='Median Salary by Region and Job Category',
                 labels={'salary_in_usd': 'Median Salary in USD', 'region': 'Region', 'job_category': 'Job Category'},
                 barmode='group')
    st.plotly_chart(fig4, use_container_width=True)

# Salary trend over years
st.subheader('Salary Trend Over Years')
yearly_salary = filtered_df.groupby('work_year')['salary_in_usd'].agg(['mean', 'median']).reset_index()
fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=yearly_salary['work_year'], y=yearly_salary['mean'],
                mode='lines+markers',
                name='Average Salary'))
fig5.add_trace(go.Scatter(x=yearly_salary['work_year'], y=yearly_salary['median'],
                mode='lines+markers',
                name='Median Salary'))
fig5.update_layout(title='Salary Trend Over Years',
                  xaxis_title='Year',
                  yaxis_title='Salary in USD')
st.plotly_chart(fig5, use_container_width=True)

# Remote work distribution
st.subheader('Remote Work Distribution')
remote_by_year = filtered_df.groupby(['work_year', 'remote_work_type']).size().unstack().apply(lambda x: x/x.sum()*100, axis=1)
fig6 = px.bar(remote_by_year, barmode='stack',
             title='Percentage of Remote Work Types by Year',
             labels={'value': 'Percentage', 'work_year': 'Year', 'remote_work_type': 'Work Type'})
st.plotly_chart(fig6, use_container_width=True)

# Top paying jobs
st.subheader('Top Paying Jobs')
top_jobs = filtered_df.groupby('job_title')['salary_in_usd'].median().sort_values(ascending=False).head(10).reset_index()
fig7 = px.bar(top_jobs, y='job_title', x='salary_in_usd',
             title='Top 10 Highest Paying Data Science Jobs',
             labels={'salary_in_usd': 'Median Salary in USD', 'job_title': 'Job Title'},
             orientation='h')
fig7.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig7, use_container_width=True)

# Raw data
st.subheader('Raw Data')
st.dataframe(filtered_df)

# Download button
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtered_ds_salaries.csv',
    mime='text/csv'
)