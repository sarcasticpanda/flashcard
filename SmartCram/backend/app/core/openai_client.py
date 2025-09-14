"""
OpenAI API client for generating flashcards and quizzes.
Handles communication with OpenAI's API for content creation.
"""

import json
import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .config import settings


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize OpenAI client with API key."""
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_flashcards(
        self, 
        topic: str, 
        source_text: str, 
        num_cards: int = 8
    ) -> List[Dict[str, str]]:
        """
        Generate flashcards from source text using OpenAI.
        
        Args:
            topic: The topic/subject for the flashcards
            source_text: The source text to generate flashcards from
            num_cards: Number of flashcards to generate (1-30)
            
        Returns:
            List[Dict[str, str]]: List of flashcards with 'question' and 'answer' keys
        """
        prompt = f"""
        You are an expert educational content creator. Create {num_cards} flashcards from the given text.
        
        Topic: {topic}
        Source Text: {source_text}
        
        Instructions:
        - Create clear, concise questions and answers
        - Questions should be specific and test understanding
        - Answers should be 1-3 sentences maximum
        - Cover key concepts from the source text
        - Ensure questions are varied (definition, application, analysis)
        
        Return ONLY a JSON array with this exact format:
        [
            {{"question": "Question text here", "answer": "Answer text here"}},
            {{"question": "Question text here", "answer": "Answer text here"}}
        ]
        
        Do not include any other text, only the JSON array.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_flashcards_json(content)
            
        except Exception as e:
            print(f"Error generating flashcards: {e}")
            return self._generate_fallback_flashcards(topic, source_text, num_cards)
    
    def generate_quiz(
        self, 
        topic: str, 
        source_text: str, 
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate a multiple-choice quiz from source text using OpenAI.
        
        Args:
            topic: The topic/subject for the quiz
            source_text: The source text to generate quiz from
            num_questions: Number of questions to generate (1-20)
            
        Returns:
            Dict[str, Any]: Quiz with title and questions
        """
        prompt = f"""
        You are an expert quiz creator. Create a {num_questions}-question multiple-choice quiz from the given text.
        
        Topic: {topic}
        Source Text: {source_text}
        
        Instructions:
        - Create challenging but fair questions
        - Each question must have exactly 4 options (A, B, C, D)
        - Only one option should be correct
        - Include a mix of difficulty levels
        - Questions should test understanding, not just memorization
        
        Return ONLY a JSON object with this exact format:
        {{
            "title": "Quiz Title Here",
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_index": 0
                }}
            ]
        }}
        
        Note: correct_index should be 0 for A, 1 for B, 2 for C, 3 for D
        Do not include any other text, only the JSON object.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_quiz_json(content, topic)
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_fallback_quiz(topic, num_questions)
    
    def _parse_flashcards_json(self, content: str) -> List[Dict[str, str]]:
        """Parse JSON response for flashcards."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                flashcards = []
                for item in data:
                    if isinstance(item, dict) and 'question' in item and 'answer' in item:
                        flashcards.append({
                            'question': str(item['question']).strip(),
                            'answer': str(item['answer']).strip()
                        })
                return flashcards[:30]  # Limit to 30 cards
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing flashcards JSON: {e}")
        
        return []
    
    def _parse_quiz_json(self, content: str, topic: str) -> Dict[str, Any]:
        """Parse JSON response for quiz."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                quiz = {
                    'title': str(data.get('title', f'Quiz: {topic}')),
                    'questions': []
                }
                
                for q in data.get('questions', []):
                    if isinstance(q, dict) and 'question' in q and 'options' in q:
                        options = list(map(str, q.get('options', [])))
                        while len(options) < 4:
                            options.append("")
                        
                        quiz['questions'].append({
                            'question': str(q['question']).strip(),
                            'options': options[:4],
                            'correct_index': int(q.get('correct_index', 0)) % 4
                        })
                
                return quiz
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error parsing quiz JSON: {e}")
        
        return self._generate_fallback_quiz(topic, 1)
    
    def _generate_fallback_flashcards(
        self, 
        topic: str, 
        source_text: str, 
        num_cards: int
    ) -> List[Dict[str, str]]:
        """Generate fallback flashcards when API fails."""
        return [
            {
                'question': f"What is the main topic of {topic}?",
                'answer': f"The main topic is {topic}."
            },
            {
                'question': f"Can you explain {topic}?",
                'answer': f"{topic} is a subject that covers various concepts and principles."
            }
        ]
    
    def _generate_fallback_quiz(self, topic: str, num_questions: int) -> Dict[str, Any]:
        """Generate fallback quiz when API fails."""
        return {
            'title': f'Quiz: {topic}',
            'questions': [
                {
                    'question': f'What is {topic}?',
                    'options': [
                        f'A subject about {topic}',
                        'An unrelated topic',
                        'A mathematical concept',
                        'A historical event'
                    ],
                    'correct_index': 0
                }
            ]
        }


# Global OpenAI client instance
openai_client = OpenAIClient()
