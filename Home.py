import requests
from PIL import Image
from google_api import user_instruction_default, system_instruction_default
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
        image = None
        streamlit.text('\n')
    # Option to convert the image to LaTeX or Text
    option = streamlit.radio('Select the type of conversion', ['LaTeX', 'Text', 'Custom'])
    streamlit.write(f"You selected: `{option}`", )
    if option == 'Custom':
        # Input text with multiple lines, with 10 as the default number of lines
        user_instruction = streamlit.text_area('Enter user instruction', value=user_instruction_default, height=300)
        system_instruction = streamlit.text_area('Enter system instruction', value=system_instruction_default, height=300)
    else:
        user_instruction = user_instruction_default
        system_instruction = system_instruction_default
    if streamlit.button('Convert'):
        if uploaded_file is not None and image is not None:
            with streamlit.spinner('Computing'):
                response = requests.post('http://127.0.0.1:8000/submit-pdf/', files={'file': uploaded_file.getvalue()}, data={'type_task': option, 'user_instruction': user_instruction or ' ', 'system_instruction': system_instruction or ' '})
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