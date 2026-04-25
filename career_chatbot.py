import streamlit as st
import time
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


class CareerChatAssistant:

    def __init__(self, career_system=None):
        """Initialize the career chat assistant with the career guidance system"""
        
        self.career_system = career_system
        self.openai_api_key = career_system.openai_api_key if career_system else None
        
        self.vector_store = None
        self.retrieval_chain = None

        self.conversation_history = []
        self.chat_history = []

        def add_to_history(self, role, message):
           """Add a message to the conversation history"""
            self.conversation_history.append({"role": role, "message": message})


        def get_formatted_history(self):
            """Get the conversation history formatted for prompt"""
            formatted = ""
            for entry in self.conversation_history:
                formatted += f"{entry['role']}: {entry['message']}\n"
            return formatted
 
    def initalize_rag(self,career_data):
        """Initialize RAG with career analysis data"""
        if not self.openai_api_key or not career_data:
            return False

        try:
            embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)

            documents = []

            if "research" in career_data:
                documents.append(f"Career Overview: {career_data['research']}")

            if "market_analysis" in career_data:
                documents.append(f"Market Analysis: {career_data['market_analysis']}")

            if "learning_roadmap" in career_data:
                documents.append(f"Learning Roadmap: {career_data['learning_roadmap']}")

            if "industry_insights" in career_data:
                documents.append(f"Industry Insights: {career_data['industry_insights']}")

            if not documents:
                return False

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            chunks = text_splitter.create_documents([" ".join(documents)])

            self.vector_store = FAISS.from_documents(chunks, embeddings)

            structured_prompt_template = """
            You are a Career Chat Assistant providing information about careers based on detailed analysis.

            Context information from career analysis:
            {context}

            Chat History:
            {chat_history}

            Human Question: {question}

            Provide a clear, concise, and structured response. Format your answer using bullet points or numbered lists where appropriate. Organize information into clear categories with headings when the answer requires multiple sections. Make the response easy to scan and understand at a glance.

            If multiple aspects need to be covered, use separate bullet points for each aspect.
            If providing steps or a process, use numbered lists.
            Use markdown formatting to enhance readability.
            Keep the answer focused and directly relevant to the question.

            Assistant Response:
            """

            structured_prompt = PromptTemplate(
                template=structured_prompt_template,
                input_variables=["context", "chat_history", "question"]
            )

            self.retrieval_chain = ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(api_key=self.openai_api_key),
                retriever=self.vector_store.as_retriever(),
                combine_docs_chain_kwargs={"prompt": structured_prompt}
            )

            return True

        except Exception as e:
            print(f"Error initializing RAG: {str(e)}")
            return False

        def process_question(self, question, career_data=None):
    """Process a user question about career data using RAG"""

    # Add user question to history
    self.add_to_history("User", question)

    # Initialize RAG if not already done
    if not self.vector_store and career_data:
        rag_success = self.initialize_rag(career_data)
        if rag_success:
            st.session_state.rag_initialized = True

    # If RAG is available, use it
    if self.retrieval_chain and st.session_state.get("rag_initialized", False):
        try:
            # Use RAG to answer the question
            result = self.retrieval_chain.invoke({
                "question": question,
                "chat_history": self.chat_history
            })

            # Update chat history
            self.chat_history.append((question, result["answer"]))

            response = result["answer"]

        except Exception as e:
            print(f"Error in RAG processing: {str(e)}")

            # Fallback if RAG fails
            response = self._fallback_processing(question, career_data)

    else:
        # Standard processing if RAG not available
        response = self._fallback_processing(question, career_data)

        # Store assistant response
         self.add_to_history("Career Assistant", response)
         return response    

    def _fallback_processing(self, question, career_data=None):
        """Fallback processing when RAG is not available"""

        if self.career_system:
            # Use the career guidance system's chat function
            return self.career_system.chat_with_assistant(question, career_data)
        else:
            # Simple keyword-based fallback with structured responses
            career_name = career_data.get("career_name", "the selected career") if career_data else "this career"

            # Salary related response
            if "salary" in question.lower() or "pay" in question.lower() or "money" in question.lower():
                return f"""
## Salary Information for {career_name}

The salary ranges vary based on several factors:

- **Entry-level positions**: $60,000–$80,000  
- **Mid-level professionals**: $80,000–$110,000  
- **Experienced professionals**: $110,000–$150,000  
- **Senior roles**: $150,000+ with additional benefits  

### Key factors affecting compensation:
- Geographic location (major tech hubs typically pay more)
- Company size and industry
- Experience and skill level
- Education and certifications
"""

        # Skills related response
        elif "skills" in question.lower() or "learn" in question.lower() or "study" in question.lower():
            return f"""
## Essential Skills for {career_name}

### Technical Skills
- Domain-specific technical knowledge  
- Relevant tools and technologies  
- Problem-solving methodologies  
- Technical documentation  

### Soft Skills
- Communication (written and verbal)  
- Collaboration and teamwork  
- Project management  
- Time management  
- Adaptability and continuous learning  

For best results, develop a balanced combination of both technical expertise and interpersonal abilities.
"""

        # Job / market related response
        elif "job" in question.lower() or "market" in question.lower():
            return f"""
## Job Market Trends for {career_name}

- Technology sector: High and consistent demand  
- Finance and healthcare: Growing adoption  
- Manufacturing and retail: Emerging opportunities  
"""

        # Daily work / lifestyle response
        elif "day" in question.lower() or "work" in question.lower() or "life" in question.lower():
            return f"""
## Typical Day as a {career_name} Professional

### Daily Activities
1. Technical work and core responsibilities  
2. Collaboration meetings with team members  
3. Problem-solving sessions  
4. Documentation and reporting  

### Work Environment
- Office or remote setup  
- Collaborative team culture  
- Fast-paced and project-based work  
"""

        # Education / career path
        else:
            return f"""
## Career Path for {career_name}

### Education
- Bachelor's degree in a relevant field  
- Master's degree (optional but beneficial)  
- PhD for research and specialized roles  

### Alternative Paths
- Bootcamps: Intensive, focused training programs  
- Self-directed learning: Online courses and projects  
- Apprenticeships/Internships: Learning through practice  

### Certifications
- Industry-specific certifications  
- Tool and technology certifications  
- Methodology certifications  

### Career Benefits
- Competitive compensation packages  
- Strong growth opportunities  
- Work with cutting-edge technologies  
- Intellectual challenges  

### Work-Life Considerations
- Flexible work options  
- Project-based workloads  
- Continuous learning and development  

Many professionals enter this field through non-traditional paths. A strong portfolio can be as valuable as formal education.
"""

def display_chat_interface(career_data=None, career_system=None):
    """Display a chat interface in the Streamlit app"""

    st.markdown(
        "<h3 style='color: #82B1FF;'>💬 Career Chat Assistant</h3>",
        unsafe_allow_html=True
    )

    # Initialize the chat assistant in session state if not already done
    if "chat_assistant" not in st.session_state:
        st.session_state.chat_assistant = CareerChatAssistant(career_system)

        # Initialize RAG with career data if available
        if career_data:
            rag_success = st.session_state.chat_assistant.initialize_rag(career_data)
            st.session_state.rag_initialized = rag_success

            if rag_success:
                st.markdown(
                    "<div style='background-color: #1B5E20; color: white; "
                    "padding: 10px; border-radius: 5px; margin-bottom: 15px;'>"
                    "✅ Enhanced chat capabilities initialized with career data</div>",
                    unsafe_allow_html=True
                )

    # Initialize messages in session state if not already done
    if "messages" not in st.session_state:
        st.session_state.messages = []

        # Add a welcome message
        career_name = career_data.get("career_name", "your selected career") if career_data else "a career"

        welcome_message = {
            "role": "assistant",
            "content": f"""
👋 Hello! I'm your Career Chat Assistant. I can answer questions about {career_name}
using the detailed analysis we've generated.

Here are some questions you might ask:
* What are the typical salary ranges for this career?
* What skills are most important for success?
* How is the job market looking?
* What does a typical day look like?
* What educational paths lead to this career?

What would you like to know?
"""
        }

        st.session_state.messages.append(welcome_message)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    user_input = st.chat_input("Ask me about this career...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            # Add a placeholder with typing animation
            message_placeholder = st.empty()
            full_response = ""

            # Process the question with the chat assistant
            with st.spinner("Searching career data for relevant information..."):
                response = st.session_state.chat_assistant.process_question(
                    user_input, career_data
                )

            # Simulate typing
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.01)  # Adjust typing speed
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response})


    

