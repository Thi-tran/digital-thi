import React from 'react';
import { Button } from './Button';
import { SuggestionButton } from '@/types';

interface SuggestionGridProps {
  suggestions: SuggestionButton[];
  onSelect: (suggestion: SuggestionButton) => void;
  isLoading?: boolean;
}

export const SuggestionGrid: React.FC<SuggestionGridProps> = ({
  suggestions,
  onSelect,
  isLoading = false,
}) => {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {suggestions.map((suggestion) => (
        <Button
          key={suggestion.id}
          variant="suggestion"
          onClick={() => onSelect(suggestion)}
          disabled={isLoading}
          className="text-left"
        >
          {suggestion.text}
        </Button>
      ))}
    </div>
  );
};

export default SuggestionGrid;
