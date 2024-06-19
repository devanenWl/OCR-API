import requests
from PIL import Image
import streamlit

if __name__ == '__main__':
    streamlit.set_page_config(page_title='LaTeX-OCR')
    streamlit.title('LaTeX OCR')
    streamlit.markdown('Convert images of equations to corresponding LaTeX code.\n\n')

    uploaded_file = streamlit.file_uploader(
        'Upload an image an equation',
        type=['pdf'],
    )

    if uploaded_file is not None:
        if uploaded_file.type == 'application/pdf':
            # Select the first page of the PDF to display
            image = True
        else:
            image = Image.open(uploaded_file)
            streamlit.image(image, caption='Uploaded image', use_column_width=True)
    else:
        streamlit.text('\n')

    if streamlit.button('Convert'):
        if uploaded_file is not None and image is not None:
            with streamlit.spinner('Computing'):
                response = requests.post('http://127.0.0.1:8000/submit-pdf/', files={'file': uploaded_file.getvalue()})
            if response.ok:
                response = response.json()
                streamlit.markdown(response['message'])
                # Create a box with copyable text
                streamlit.code(response['task_id'], language='text')
                # streamlit.code(latex_code, language='latex')
                # streamlit.markdown(f'$\\displaystyle {latex_code}$')
                #
            else:
                streamlit.error(response.text)
        else:
            streamlit.error('Please upload an image.')