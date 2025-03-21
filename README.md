#AIretire: Simplifying Seniors Life, One Service at a Time

## About the Project

AIretire is a senior-centric digital assistant that combines secure document management, AI-driven form processing, and empathetic interactions. Built with Streamlit and Azure AI services, it features a sophisticated prompt pre-processing layer that auto-corrects inputs, redacts sensitive data, and validates prompts to ensure safe, accurate, and optimized communication. With voice/form hybrid interfaces, fraud detection, and accessibility tools (text-to-speech, high-contrast mode), AIretire delivers trustworthy retirement services and is designed to scale into a unified "digital file cabinet" for seniors’ critical needs.

### 🏆 Microsoft AI Innovation Challenge Submission

**Executive Challenge Category**: Auto-Correct and Prompt Validation Before AI Execution

### 🎯 Contexttual Challenges

Seniors often encounter unique challenges in managing their personal and financial information, including:

- Difficulty with technical terminology
- Increased vulnerability to financial fraud
- Need for clear, accurate communication
- Concerns about Privacy and security 

Our solution implements a multi-layered prompt processing system that:

- Auto-corrects and validates user inputs
- Protects sensitive information
- Ensures clear and ethical AI responses
- Provides accessible interface options

## 🏆 Competition Alignment - Judging Criteria Implementation

| Criteria           | Our Implementation                                                      |
| ------------------ | ----------------------------------------------------------------------- |
| **Performance**    | Multi-stage validation pipeline input correction                        |
| **Innovation**     | Senior-specific term optimization + voice-form hybrid interaction model |
| **Azure Usage**    | Multiple Azure Services Integrated                                      |
| **Responsible AI** | Real-time PII redaction + ethical response guidelines                   |

**Technologies Used**
Frontend: Streamlit for building the user interface.
Backend: Python for application logic and data processing.

**Azure Services**:
  - Azure Computer Vision: Analyzes and processes images, including document uploads, ensuring quality and integrity.
  - Azure Speech Services: Enables voice interaction and text-to-speech capabilities, allowing users to engage with the application naturally.
  - Azure Text Analytics: Extracts insights from user inputs, including:
    - Entity Recognition: Identifies and extracts entities from user inputs.
    - PII Detection: Automatically detects sensitive information to protect user privacy.
  - Azure Content Safety API: Provides real-time validation of user inputs to ensure safety and compliance by analyzing for harmful content.
  - Azure Document Intelligence: Extracts and processes structured data from various document types, facilitating efficient handling of user-uploaded documents.

**Other Technologies**:
Google Gemini: Utilized for advanced AI capabilities, specifically the Gemini-1.5-Pro model.
LanguageTool Library: A custom implementation for grammar correction, enhancing the clarity of user inputs.

## 🎥 Demo & Presentation

- [Demo Video](https://drive.google.com/file/d/1806oj9cxQoEMICQth4me_MvIq31E_-Wu/view?usp=sharing)
- [Presentation](link_to_presentation) - Coming soon

## 🎯 Project Goals

1. Create a secure and accessible platform for senior services and personal management.
2. Implement comprehensive prompt validation and correction
3. Ensure responsible AI practices and ethical handling of sensitive data
4. Provide multi-modal interaction (text, voice, form-filling)

## 🛠 Solution Components

### Core Features

1. **Intelligent Input Processing**
   - **Description**: This feature ensures that user inputs are accurate and contextually relevant, enhancing the overall user experience.
   - **Grammar and spelling correction**: Automatically corrects common errors to improve clarity and professionalism in user submissions.
   - **Context-aware term optimization**: Adapts terminology based on user profiles and preferences, making interactions more intuitive.
   - **Multi-language support**: Allows users to interact in their preferred language, increasing accessibility for diverse user groups.

2. **Safety & Security**
   - **Description**: Focused on protecting user data and ensuring safe interactions within the application.
   - **PII detection and redaction**: Identifies and removes personally identifiable information from user inputs to safeguard privacy.
   - **Harmful content filtering**: Analyzes user prompts for inappropriate or dangerous language, maintaining a safe environment.
   - **Ethical language validation**: Ensures that responses are appropriate and sensitive to the needs of senior users.

3. **Accessibility**
   - **Description**: Designed to make the application usable for all seniors, regardless of their abilities or preferences.
   - **Voice input/output**: Enables hands-free interaction, allowing users to communicate with the application using natural language.
   - **Adjustable text size**: Users can modify text size for better readability, accommodating those with visual impairments.
   - **High contrast mode**: Enhances visibility for users with low vision by providing a stark contrast between text and background.
   - **Clear error messaging**: Provides straightforward feedback on errors, helping users understand and correct issues easily.

## 🏗 Architecture

### Input Processing Flow

```
User Input → Pre-processing → Validation → AI Processing → Response
   ↓             ↓              ↓              ↓            ↓
Voice/Text → Correction → Safety Check → Optimization → Delivery
```

### Secure Input Processing Pipeline

    A[Raw Input] --> B{Grammar Check}
    B --> C[PII Detection]
    C --> D[Context Optimization]
    D --> E[Safety Filter]
    E --> F[AI Response]
    F --> G[Accessibility Formatting]

## 🎓 Key Learnings

1. **Technical Insights**

   - Effective prompt pre-processing significantly improves AI response quality
   - Multi-modal input requires specialized validation approaches
   - Azure services integration provides robust security features

2. **User Experience**

   - Senior users benefit from clear, immediate feedback
   - Voice interaction enhances accessibility
   - Simplified interface improves engagement

3. **Security & Ethics**
   - Proactive PII detection is crucial
   - Ethical language validation requires context
   - Balance between security and usability

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.8+
Azure Subscription
Required Python packages (see requirements.txt)
```

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/AIretire.git
cd AIretire
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure Azure credentials

```bash
# Create .env file with:
AZURE_SUBSCRIPTION_KEY=your_key
AZURE_REGION=your_region
```

4. Run the application

```bash
streamlit run airetire.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

_This project was developed for the Microsoft AI Innovation Challenge 2025_
