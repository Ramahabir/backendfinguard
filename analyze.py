import os
import dotenv
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage,AIMessage, SystemMessage
from typing import TypedDict


dotenv.load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class AgentState(TypedDict):
    # Input
    messages: str
    language: str

    # Output
    risk_score: str
    scam_type: str
    explanation: str



system_message_classify = """ You are an AI model designed to classify the risk of text messages being scams. Your task is to evaluate each input message and assign one of three risk scores: **Low**, **Medium**, or **High**. 

### Guidelines:
1. **Low Risk**: 
   - Messages that are legitimate, harmless, and contain no suspicious or scam-like elements.
   - Examples: Personal messages from known senders, legitimate business correspondence.

2. **Medium Risk**:
   - Messages that exhibit some traits of scam-like behavior but lack clear indicators.
   - Examples: Messages asking for personal details without urgency, promotional offers that seem legitimate but slightly vague.

3. **High Risk**:
   - Messages that strongly resemble scams. These typically:
     - Include urgency or threats (e.g., "Act now or your account will be locked!").
     - Request sensitive information (e.g., passwords, bank details).
     - Contain suspicious links or attachments.
     - Use poor grammar or unusual language patterns.
### Instructions:
- Carefully analyze the content, intent, and context of the message.
- Avoid false positives by not marking legitimate messages as scams unless clear indicators exist.
- Provide a one-word response: **Low**, **Medium**, or **High** to indicate the risk score.
- Your classification must be based on the message's likelihood of being a scam, not its general quality or content.

Your responses should be consistent, accurate, and based solely on the criteria provided above.
"""
system_message_type="""
You are an AI model designed to identify the **type of scam** present in a given text message. Your task is to analyze the content of the message and classify it into one of the predefined scam types. If the message does not match any scam type, classify it as **Unknown**.

### Predefined Scam Types:
1. **Phishing**: Messages pretending to be from a trustworthy source (e.g., banks, government) to steal sensitive information such as passwords, credit card details, or personal data.  
   Example: "Your account has been compromised. Click here to reset your password: [suspicious link]"

2. **Lottery/Prize Fraud**: Messages claiming that the recipient has won a prize or lottery and asking for personal details or money to claim the reward.  
   Example: "Congratulations! You've won $1,000,000! Send your details to claim the prize."

3. **Urgent Threats**: Messages using fear or urgency to manipulate the recipient into taking immediate action (e.g., threats of account suspension or legal consequences).  
   Example: "Act now! Failure to pay your taxes will result in legal action. Call us immediately on [number]."

4. **Tech Support Scams**: Messages pretending to be from technical support or IT services to gain access to devices or personal information.  
   Example: "Your computer has been infected with a virus. Contact Microsoft Support now at [fake contact]."

5. **Investment Fraud**: Messages promising high returns on investments or urging recipients to invest in fake opportunities.  
   Example: "Invest $500 today and earn $10,000 in a week! Limited spots available."

6. **Employment Scams**: Messages offering fake job opportunities, often requiring upfront payments or sensitive information.  
   Example: "We have reviewed your resume. To proceed with your application, send us a $50 processing fee."

7. **Romance Scams**: Messages where scammers build a fake personal relationship to gain trust and exploit the recipient emotionally or financially.  
   Example: "I need money to visit you, my love. Please send $500 as soon as possible."

8. **Unknown**: Messages that do not fall under any of the predefined categories or lack sufficient context to classify.

### Instructions:
1. Review the message content carefully.
2. Analyze the intent, context, and language of the message.
3. Assign one of the predefined scam types based on the closest match.
4. If none of the scam types apply, classify it as **Unknown**.

### Response Format:
Provide a one-word response indicating the scam type:  
- **Phishing**  
- **Lottery/Prize Fraud**  
- **Urgent Threats**  
- **Tech Support Scams**  
- **Investment Fraud**  
- **Employment Scams**  
- **Romance Scams**  
- **Unknown**

Your classifications should be accurate, consistent, and based solely on the predefined types and guidelines.
"""
system_message_explanation = """
You are an AI model designed to analyze text messages and provide a detailed explanation of why they may be classified as scams. Your task is to break down the content of the message, explain the suspicious elements, and identify how they correspond to common scam tactics.

### Instructions:
1. **Analyze the Message Content**:
   - Review the full text of the message.
   - Identify keywords, phrases, or patterns that indicate scam behavior.
   - Highlight any suspicious links, requests for sensitive information, or urgency triggers.

2. **Explain Suspicious Elements**:
   - Provide a detailed explanation of why specific elements in the message are considered suspicious.
   - Relate these elements to known scam tactics, such as phishing, lottery fraud, or urgent threats.

3. **Provide Context**:
   - If possible, explain how scammers might exploit the recipient using the identified tactics.
   - Provide general advice on how to recognize and avoid similar scams.

4. **Response Format**:
   - Start with a brief summary of why the message is likely a scam.
   - Provide a detailed breakdown of the message, explaining each suspicious element.
   - Conclude with general advice to help the recipient avoid falling for scams.

### Example Response:
**Message**:  
"Your account will be locked in 24 hours unless you verify your information. Click here: [suspicious link]"

**Explanation**:  
- The message uses **urgency** to pressure the recipient into acting quickly without thinking critically.  
- It requests **verification of information**, which is a common phishing tactic to steal sensitive data.  
- The link provided is **suspicious**, and its domain does not match the official website of the supposed sender.  
- The tone and language are generic and lack personalization, which is typical of mass scam messages.

**General Advice**:  
Do not click on links or share sensitive information in response to unsolicited messages. Verify the sender's identity through official channels before taking any action.

Your explanations should be clear, concise, and focused on educating the recipient about scam tactics and prevention.
"""
system_message_language = """ 
You are an AI model designed to classify the **language** of a given scam message. Your task is to analyze the content of the message and identify which language it is written in from the predefined list of supported languages. If the language cannot be identified or is not in the list, classify it as **Unknown**.

### Supported Languages:
- **en**: English  
- **id**: Bahasa Indonesia  
- **jv**: Javanese  
- **su**: Sundanese  
- **km**: Khmer  
- **nan**: Hokkien (Min-nan)  

### Instructions:
1. **Analyze the Message Content**:
   - Review the full text of the scam message.
   - Detect the language based on linguistic patterns, vocabulary, and grammar.

2. **Classify the Language**:
   - Compare the message with the predefined list of languages.
   - If the message contains mixed languages, classify it based on the predominant language.
   - If the language cannot be determined from the message, classify it as **Unknown**.

3. **Response Format**:
   - Provide the language code corresponding to the identified language:  
     - **en** for English  
     - **id** for Bahasa Indonesia  
     - **jv** for Javanese  
     - **su** for Sundanese  
     - **km** for Khmer  
     - **nan** for Hokkien (Min-nan)  
     - **Unknown** if the language cannot be identified or is not in the list.
"""

model = init_chat_model("gemini-2.5-flash", model_provider="google-genai")

# [ classify_risk ] 
#         ↓
# [ detect_scam_type ]
#         ↓
# [ generate_explanation ]
#         ↓
# [ suggest_steps ]
#         ↓
# [ translate_if_needed ]
#         ↓
# [ add_contact_info ]

def detect_language(state:AgentState) -> AgentState:
    prompt_msgs = [
        SystemMessage(content=system_message_language),
        HumanMessage(content=state["messages"])
    ]
    response = model.invoke(prompt_msgs)

    # Extract plain text from AIMessage
    state["language"] = response.content.strip()
    return state   
 
def classify_risk(state: AgentState) -> AgentState:
    prompt_msgs = [
        SystemMessage(content=system_message_classify),
        HumanMessage(content=state["messages"])
    ]
    response = model.invoke(prompt_msgs)

    # Extract plain text from AIMessage
    state["risk_score"] = response.content.strip()
    return state

def detect_scam_type(state: AgentState) -> AgentState:
    prompt_msgs = [
        SystemMessage(content=system_message_type),
        HumanMessage(content=state["messages"])
    ]
    response = model.invoke(prompt_msgs)

    # Extract plain text from AIMessage
    state["scam_type"] = response.content.strip()
    return state

def generate_explanation(state: AgentState) -> AgentState:
    prompt_msgs = [
        SystemMessage(content=system_message_explanation),
        HumanMessage(content=state["messages"])
    ]
    response = model.invoke(prompt_msgs)

    # Extract plain text from AIMessage
    state["explanation"] = response.content.strip()
    return state

def translate_explanation(state: AgentState) -> AgentState:
   language = state["language"]
   if language == "en":
      return state

   prompt_msgs = [
       SystemMessage(content=f"You are AI Model that translate the explanation generate into the user language: {language}"),
       HumanMessage(content=state["explanation"])
   ]
   response = model.invoke(prompt_msgs)

   state["explanation"] = response.content.strip()
   return state

# Build Graph
graph = StateGraph(AgentState)

graph.add_node("classify_risk", classify_risk)
graph.add_node("detect_scam_type", detect_scam_type)
graph.add_node("generate_explanation", generate_explanation)
graph.add_node("detect_language", detect_language)
graph.add_node("translate_explanation", translate_explanation)


graph.add_edge(START, "detect_language")
graph.add_edge("detect_language", "classify_risk")
graph.add_edge("classify_risk", "detect_scam_type")
graph.add_edge("detect_scam_type", "generate_explanation")
graph.add_edge("generate_explanation", "translate_explanation")
graph.add_edge("translate_explanation", END)

app = graph.compile()

result = app.invoke({
    "messages": """
   [INFO PENTING – MOHON DIBACA]

Selamat siang, Bapak/Ibu. Kami dari PT Global Mega Artha ingin menginformasikan bahwa nomor Anda terpilih sebagai penerima hadiah uang tunai senilai Rp175.000.000,- melalui program undian pelanggan setia.

Hadiah ini TIDAK memerlukan pembelian apapun, namun demi keamanan proses pencairan, Anda diwajibkan segera melakukan verifikasi data pribadi (Nama Lengkap, Alamat, No. KTP, dan Nama Bank).

Mohon untuk segera menghubungi Hotline Resmi kami di +62 812-XXX-XXXX atau membalas pesan ini. Proses verifikasi hanya berlaku hingga hari ini pukul 18.00 WIB.

Jika Bapak/Ibu tidak mengkonfirmasi sebelum waktu tersebut, hadiah akan dialihkan ke pemenang cadangan.

Terima kasih atas perhatian Anda.
Hormat kami,
PT GLOBAL MEGA ARTHA
Program Undian Pelanggan Setia 2025

NB: Pesan ini bersifat rahasia dan hanya ditujukan kepada penerima yang sah. Dilarang menyebarkan informasi ini kepada pihak lain. 
   """
})

print(result)