'use client';

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip
} from '@mui/material';

interface SearchResult {
  platform: string;
  username: string;
  text: string;
  timestamp: string;
  sentiment?: {
    label: string;
    score?: number;
  };
}

interface SearchResultsProps {
  results: SearchResult[];
}

export default function SearchResults({ results }: SearchResultsProps): React.ReactElement | null {
  if (!results.length) {
    return null;
  }

  return (
    <Box sx={{ mt: 3 }}>
      <Typography variant="h6" gutterBottom>
        Search Results
      </Typography>
      {results.map((result) => (
        <Card key={`${result.platform}-${result.username}-${result.timestamp}`} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="subtitle2" color="text.secondary">
              {result.platform} • {result.username}
            </Typography>
            <Typography variant="body1">{result.text}</Typography>
            <Typography variant="caption" color="text.secondary">
              {result.timestamp}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip
                icon={
                  result.sentiment?.label?.toLowerCase() === 'positive'
                    ? <span role="img" aria-label="positive">😊</span>
                    : result.sentiment?.label?.toLowerCase() === 'negative'
                    ? <span role="img" aria-label="negative">😞</span>
                    : <span role="img" aria-label="neutral">😐</span>
                }
                label={
                  result.sentiment?.label
                    ? `Sentiment: ${result.sentiment.label} (${result.sentiment.score ? (result.sentiment.score * 100).toFixed(1) : 'N/A'}%)`
                    : 'Sentiment: N/A'
                }
                color={
                  result.sentiment?.label?.toLowerCase() === 'positive'
                    ? 'success'
                    : result.sentiment?.label?.toLowerCase() === 'negative'
                    ? 'error'
                    : 'default'
                }
                variant="outlined"
                size="small"
              />
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
} 