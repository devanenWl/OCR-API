import streamlit
import requests
if __name__ == '__main__':
    streamlit.set_page_config(page_title='Status')
    streamlit.title('Status')
    streamlit.markdown('Check the status of the API and Celery worker.\n\n')
    # Create a box to input the task ID and a button to check the status
    task_id = streamlit.text_input('Task ID')
    if streamlit.button('Check status') or task_id:
        response = requests.get(f'http://localhost:8000/check-status/{task_id}')
        if response.ok:
            response = response.json()
            if response['status'] == 'complete':
                streamlit.success('Processing complete')
                # Display the result as latex
                streamlit.code(response['result'], language='latex')
            else:
                streamlit.warning('Processing in progress ', response['processed_pages'], 'out of', response['total_pages'], 'pages processed')
                streamlit.code(response['result'], language='latex')
            # streamlit.write(response)
        else:
            streamlit.error(response.text)