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

- [Demo Video](link_to_demo) - Coming soon
- [Presentation](link_to_presentation) - Coming soon

## 🎯 Project Goals

1. Create a secure and accessible platform for retirement services
2. Implement comprehensive prompt validation and correction
3. Ensure responsible AI practices and ethical handling of sensitive data
4. Provide multi-modal interaction (text, voice, form-filling)

## 🛠 Solution Components

### Core Features

1. **Intelligent Input Processing**

   - Grammar and spelling correction
   - Context-aware term optimization
   - Multi-language support

2. **Safety & Security**

   - PII detection and redaction
   - Harmful content filtering
   - Ethical language validation

3. **Accessibility**
   - Voice input/output
   - Adjustable text size
   - High contrast mode
   - Clear error messaging

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
