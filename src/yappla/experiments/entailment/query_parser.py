from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
import re
from query import Query, QueryType, Result


@dataclass
class KBCommand:
    command: str  # "KB", "LOAD KB", "BEGIN KB", "END KB"
    content: Optional[str] = None

class QueryParser:
    """Parser for multiline query strings."""
    
    QUERY_TYPES = {
        "ENTAIL": QueryType.ENTAIL,
        "CONSISTENT": QueryType.CONSISTENT,
        "EXPLAIN": QueryType.EXPLAIN,
        "LABEL": QueryType.LABEL,
        "POSSIBLE": QueryType.POSSIBLE,
        "INDUCE": QueryType.INDUCE,
    }
    
    KB_COMMANDS = ["LOAD KB", "BEGIN KB", "END KB", "KB"]  # Longer patterns first
    
    KEYWORDS = ["SUBJECT TO", "TIME", "GIVEN", "OPTIONS"]  # Longer patterns first
    
    def parse(self, text: str) -> Union[Query, KBCommand]:
        """
        Parse a multiline string into a Query or KBCommand.
        
        Args:
            text: The multiline string to parse
            
        Returns:
            Either a Query object or a KBCommand object
            
        Raises:
            ValueError: If the text cannot be parsed
        """
        # Normalize whitespace: collapse multiple spaces/newlines to single space
        text = re.sub(r'\s+', ' ', text.strip())
        
        if not text:
            raise ValueError("Empty input string")
        
        # Check for KB commands first (case-insensitive)
        text_upper = text.upper()
        
        for kb_cmd in self.KB_COMMANDS:
            if text_upper.startswith(kb_cmd):
                # Extract content after the KB command
                remaining = text[len(kb_cmd):].strip()
                return KBCommand(command=kb_cmd, content=remaining if remaining else None)
        
        # Parse as Query
        return self._parse_query(text)
    
    def _parse_query(self, text: str) -> Query:
        """Parse text as a Query object."""
        text_upper = text.upper()
        
        # Extract query type from beginning
        query_type = None
        remaining_text = text
        
        for type_str, type_enum in self.QUERY_TYPES.items():
            if text_upper.startswith(type_str):
                query_type = type_enum
                # Remove the query type to get remaining content
                remaining_text = text[len(type_str):].strip()
                break
        
        if query_type is None:
            raise ValueError(f"Unknown query type. Must start with one of: {', '.join(self.QUERY_TYPES.keys())}")
        
        # Parse the remaining content for keywords
        parts = self._extract_keyword_sections(remaining_text)
        
        # The first part (before any keyword) is the question
        question = parts.get('question', '').strip()
        
        if not question:
            raise ValueError("Query must contain a question")
        
        # Parse TIME if present
        time = None
        if 'TIME' in parts:
            time_str = parts['TIME'].strip()
            try:
                time = int(time_str)
            except ValueError:
                raise ValueError(f"Invalid time value: {time_str}")
        
        # Parse GIVEN and OPTIONS
        given = self._parse_dict_content(parts.get('GIVEN', '')) if 'GIVEN' in parts else None
        options = self._parse_dict_content(parts.get('OPTIONS', '')) if 'OPTIONS' in parts else None
        
        # Parse SUBJECT TO
        subject_to = parts.get('SUBJECT TO', '').strip() if 'SUBJECT TO' in parts else None
        if subject_to == '':
            subject_to = None
        
        return Query(
            type=query_type,
            question=question,
            time=time,
            given=given,
            options=options,
            subject_to=subject_to
        )
    
    def _extract_keyword_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections based on keywords (SUBJECT TO, TIME, GIVEN, OPTIONS).
        Returns a dict with section names as keys and content as values.
        Keywords can have varying amounts of whitespace (e.g., "SUBJECT TO" can be "SUBJECT  TO").
        """
        sections = {}
        text_upper = text.upper()
        
        # Find all keyword positions
        keyword_positions = []
        
        for keyword in self.KEYWORDS:
            # Create a regex pattern that allows any whitespace between words in the keyword
            keyword_pattern = r'\b' + r'\s+'.join(re.escape(word) for word in keyword.split()) + r'\b'
            
            for match in re.finditer(keyword_pattern, text_upper):
                start_pos = match.start()
                end_pos = match.end()
                keyword_positions.append((start_pos, end_pos, keyword))
        
        # Sort by position
        keyword_positions.sort(key=lambda x: x[0])
        
        # Extract content before first keyword as question
        if keyword_positions:
            sections['question'] = text[:keyword_positions[0][0]].strip()
        else:
            sections['question'] = text.strip()
            return sections
        
        # Extract content for each keyword section
        for i, (start_pos, end_pos, keyword) in enumerate(keyword_positions):
            # Content starts after this keyword ends
            content_start = end_pos
            
            # Content ends at the start of next keyword or end of string
            if i + 1 < len(keyword_positions):
                content_end = keyword_positions[i + 1][0]
            else:
                content_end = len(text)
            
            content = text[content_start:content_end].strip()
            sections[keyword] = content
        
        return sections
    
    def _parse_dict_content(self, content: str) -> Dict[str, Any]:
        """
        Parse dictionary-like content. 
        Simple implementation - can be extended for more complex parsing.
        """
        if not content:
            return {}
        
        # Try to evaluate as Python dict literal
        try:
            result = eval(content)
            if isinstance(result, dict):
                return result
        except:
            pass
        
        # Fallback: return as single-entry dict
        return {"value": content}