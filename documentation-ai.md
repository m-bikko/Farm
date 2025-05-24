# AI Response Documentation - AI Interview Platform

## Overview

This document provides comprehensive documentation on how AI responses work in the AI Interview platform. The system uses Google's Gemini 1.5 Flash model to generate intelligent feedback on interview answers and CV reviews.

## Architecture Overview

The AI response system consists of several key components:

1. **Gemini Service Layer** (`app/services/gemini_service.py`)
2. **Interview Service Layer** (`app/services/interview_service.py`)
3. **Transcription Service** (`app/services/transcription_service.py`)
4. **Interview Route Handlers** (`app/routes/interview.py`)

## Core Components

### 1. Gemini Service (`app/services/gemini_service.py`)

The `GeminiService` class is the core AI interface that handles all interactions with Google's Gemini API.

#### Key Features:
- **Model Configuration**: Uses `gemini-1.5-flash-latest` model
- **API Key Management**: Secure handling of Google API credentials
- **Error Handling**: Robust error handling with retry logic for rate limits
- **Prompt Engineering**: Structured prompts for different AI tasks

#### Main Methods:

##### `generate_review(prompt_text, safety_settings=None, generation_config=None, retries=2)`
- Core method for generating AI content
- Handles rate limiting with exponential backoff
- Returns generated text or error messages
- Default configuration: temperature=0.7, max_output_tokens=2048

##### `create_interview_review_prompt(question, answer, profession, grade)`
- Creates structured prompts for interview answer evaluation
- Evaluates on 5 criteria: Technical Accuracy, Relevance, Clarity, Completeness, Structure
- Returns formatted feedback with strengths, improvements, and technical score (1.0-5.0)

##### `create_cv_review_prompt(cv_text)`
- Creates prompts for CV/resume analysis
- Focuses on IT industry relevance
- Analyzes content, structure, keywords, and formatting

### 2. Interview Service (`app/services/interview_service.py`)

The `InterviewService` orchestrates the complete interview workflow, integrating AI services with business logic.

#### Key Workflow Methods:

##### `create_interview(user_id, profession_id, grade)`
- Creates new interview sessions
- Selects 5 random questions based on profession and grade
- Creates answer placeholders in database

##### `process_answer(answer_id, audio_path)`
This is the core AI processing method that:
1. **Retrieves Context**: Gets question, interview, and profession data
2. **Transcribes Audio**: Uses `TranscriptionService` to convert audio to text
3. **Generates AI Feedback**: Calls `GeminiService.review_interview_answer()`
4. **Extracts Rating**: Parses technical score from AI feedback using regex
5. **Stores Results**: Saves transcription, feedback, and rating to database
6. **Checks Completion**: Determines if interview is complete and calculates overall rating

##### `_check_interview_completion(interview)`
- Monitors interview progress
- Calculates overall rating as average of individual answer ratings
- Marks interview as completed when all answers are processed

### 3. Transcription Service (`app/services/transcription_service.py`)

Handles audio-to-text conversion using Gemini's multimodal capabilities.

#### Key Features:
- **Audio Format Support**: WebM, M4A, MP3, WAV, OGG, FLAC
- **File Validation**: Checks file existence and size
- **MIME Type Detection**: Proper content type handling for different audio formats
- **Error Handling**: Graceful fallbacks for transcription failures

#### Transcription Process:
1. Validates audio file existence and size
2. Determines MIME type based on file extension
3. Reads audio file as binary data
4. Sends to Gemini with transcription prompt
5. Returns clean transcribed text

### 4. Interview Routes (`app/routes/interview.py`)

Web interface endpoints that trigger AI processing.

#### Key Endpoints:

##### `/interview/submit_answer/<int:answer_id>` (POST)
Main endpoint for answer submission:
1. **File Upload**: Handles audio file upload with validation
2. **Security Check**: Verifies user ownership of answer
3. **File Processing**: Saves uploaded audio file
4. **AI Processing**: Calls `interview_service.process_answer()`
5. **Response**: Returns JSON with feedback, rating, and next URL

## AI Response Generation Workflow

### Complete Interview Answer Processing Flow:

```
1. User Records Audio Answer
   ↓
2. Audio Upload (interview.py:submit_answer)
   ↓
3. File Validation & Storage
   ↓
4. InterviewService.process_answer()
   ├─ 4a. Load Question/Interview Context
   ├─ 4b. Audio Transcription (TranscriptionService)
   │     ├─ File validation
   │     ├─ MIME type detection
   │     ├─ Gemini API call for transcription
   │     └─ Return transcribed text
   ├─ 4c. AI Feedback Generation (GeminiService)
   │     ├─ Create structured prompt with:
   │     │   • Question text
   │     │   • Transcribed answer
   │     │   • Profession context
   │     │   • Grade level
   │     ├─ Gemini API call for review
   │     └─ Return structured feedback
   ├─ 4d. Rating Extraction (Regex parsing)
   ├─ 4e. Database Storage
   └─ 4f. Interview Completion Check
   ↓
5. Return Results to User Interface
```

## Prompt Engineering

### Interview Answer Review Prompt Structure:

```
**Profession:** {profession}
**Grade Level:** {grade}
**Interview Question:** "{question}"
**Candidate's Answer (Transcribed Audio):** "{answer}"

**Instructions for AI Analysis:**
Act as an experienced IT interviewer for the specified role and level.
Evaluate based on:
1. Technical Accuracy
2. Relevance  
3. Clarity and Conciseness
4. Completeness
5. Structure

**Output Format:**
**Overall Assessment:** [1-2 sentence summary]
**Strengths:**
- [Specific strengths]
**Areas for Improvement:**
- [Specific weaknesses and suggestions]
**Technical Score (Estimate):** [1.0-5.0 score]
```

### CV Review Prompt Structure:

```
**Extracted CV Text:**
--- Start of CV Text ---
{cv_text}
--- End of CV Text ---

**Instructions for AI Analysis:**
Act as an experienced IT recruiter and career advisor.

**Output Format:**
**Overall Impression:** [2-3 sentence summary]
**Strengths:**
- [Strong points and achievements]
**Weaknesses / Areas for Improvement:**
- [Missing elements and suggestions]
**Clarity and Formatting (Inferred):** [Readability assessment]
**Keywords and Relevance:** [IT keyword analysis]
```

## Configuration

### Environment Variables Required:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Model Configuration:
- **Model**: `gemini-1.5-flash-latest`
- **Temperature**: 0.7 (balances creativity and consistency)
- **Max Output Tokens**: 2048
- **Retry Logic**: 2 retries with exponential backoff

### File Upload Limits:
- **Audio Files**: Maximum 10MB
- **Supported Formats**: MP3, WAV, OGG, FLAC, WebM, M4A
- **Storage Location**: `uploads/audio/` directory

## Database Schema Integration

### Key Tables:
- **interviews**: Stores interview sessions with overall_rating
- **answers**: Stores individual responses with transcribed_text, feedback, rating
- **questions**: Predefined questions by profession and grade
- **professions**: Available job roles

### Rating System:
- **Individual Ratings**: 1.0 to 5.0 (extracted from AI feedback)
- **Overall Rating**: Average of all answer ratings
- **Completion Tracking**: Interview marked complete when all answers processed

## Error Handling

### AI Service Error Types:
1. **API Errors**: Rate limits, authentication failures
2. **Content Blocking**: Safety filter rejections
3. **Network Issues**: Connectivity problems
4. **Transcription Failures**: Audio quality issues

### Fallback Strategies:
- Retry logic with exponential backoff for rate limits
- Graceful error messages for users
- Fallback text for transcription failures
- Continued operation even if AI components fail

## Performance Considerations

### Optimization Features:
- **Single API Configuration**: Global configuration prevents multiple setups
- **Efficient File Handling**: Stream processing for large audio files
- **Database Optimization**: Efficient queries for interview data
- **Error Caching**: Prevents repeated failed API calls

### Monitoring Points:
- API response times and success rates
- Audio transcription accuracy
- Rating distribution analysis
- User completion rates

## Security Measures

### Data Protection:
- **API Key Security**: Environment variable storage
- **File Upload Validation**: Type and size restrictions
- **User Authorization**: Ownership verification for all operations
- **Audio File Cleanup**: Temporary file management

### AI Safety:
- **Content Filtering**: Gemini's built-in safety settings
- **Prompt Injection Protection**: Structured prompt templates
- **Response Validation**: Basic sanity checks on AI outputs

## Usage Examples

### Starting an Interview:
```python
# Create new interview
interview, error = interview_service.create_interview(
    user_id=1, 
    profession_id=2, 
    grade="Middle"
)
```

### Processing an Answer:
```python
# Process audio answer
answer, error = interview_service.process_answer(
    answer_id=5, 
    audio_path="/path/to/audio.webm"
)
```

### Direct AI Review:
```python
# Generate review directly
feedback = gemini_service.review_interview_answer(
    question="What is REST API?",
    answer="REST is a architectural style...",
    profession="Backend Developer",
    grade="Junior"
)
```

## Troubleshooting

### Common Issues:

1. **API Key Not Set**: Check GOOGLE_API_KEY environment variable
2. **Rate Limiting**: Implement exponential backoff (already included)
3. **Audio Transcription Fails**: Check file format and size
4. **Empty AI Responses**: Verify prompt structure and content safety
5. **Database Errors**: Check answer ownership and foreign key constraints

### Debug Logging:
- Enable detailed logging in `app/services/` modules
- Monitor API call frequency and response times
- Track user interaction patterns

## Future Enhancements

### Potential Improvements:
1. **Advanced Prompt Engineering**: More sophisticated evaluation criteria
2. **Multi-language Support**: International interview capabilities
3. **Custom Models**: Fine-tuned models for specific domains
4. **Real-time Processing**: Streaming audio transcription
5. **Analytics Dashboard**: AI performance monitoring
6. **A/B Testing**: Prompt optimization experiments

This documentation provides a complete overview of how AI responses work in the platform, from audio upload to final feedback generation.