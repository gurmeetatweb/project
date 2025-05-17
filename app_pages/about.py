import streamlit as st
from PIL import Image

def show_about_page(df):
    
    
    st.title("About the Developer")
    
    # Developer photo (replace with your image path)
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            developer_img = Image.open(".\image\profile.png")  # or your image path
            st.image(developer_img, width=200)
        except FileNotFoundError:
            st.image("https://via.placeholder.com/200", width=200)
    
    with col2:
        st.header("Gurmeet Singh")
        st.write("""
        **Data Scientist | Full Stack Developer | AI Enthusiast**
        
        Passionate about building data-driven solutions and transforming complex data 
        into actionable insights. Specializing in Python, Machine Learning, and Cloud Technologies.
        """)
    
    # Contact Information
    st.subheader("Contact Information")
    st.write("📧 Email: [gurmeetatweb@gmail.com](mailto:gurmeetatweb@gmail.com)")
    st.write("📱 Phone: +91 81463-88887")
    
    # Social Links
    st.subheader("Connect With Me")
    st.markdown("""
    - [LinkedIn Profile](https://www.linkedin.com/in/gurmeetatweb/)
    - [GitHub Portfolio](https://github.com/gurmeetatweb)
    """)
    
    # Skills Section
    st.subheader("Technical Skills")
    st.write("""
    - **Languages:** Python, JavaScript, SQL
    - **Data Science:** Pandas, NumPy, Scikit-learn
    - **Web Development:** Streamlit, Flask, React
    - **Cloud:** AWS, GCP, Azure
    - **DevOps:** Docker, Kubernetes, CI/CD
    """)

if __name__ == "__main__":
    about_us_page()