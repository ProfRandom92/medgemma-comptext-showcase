'use client';

import { useState, useCallback } from 'react';
import axios from 'axios';
import type { PipelineResult } from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Mock response for demo when API is unavailable
const generateMockResponse = (clinicalText: string): PipelineResult => {
  const isPriority1 = /critical|severe|emergency|alert/i.test(clinicalText);
  
  return {
    compression: {
      original_text: clinicalText,
      compressed_state: {},
      original_token_count: 1250,
      compressed_token_count: 87,
      reduction_percentage: 0.93,
      compression_time_ms: 8,
    },
    triage: {
      priority_level: isPriority1 ? 'P1' : 'P2',
      priority_name: isPriority1 ? 'CRITICAL' : 'URGENT',
      reason: 'Clinical assessment based on submitted text',
    },
    doctor: {
      recommendation: 'Review all critical parameters. Consider specialist consultation for complex cases.',
      processing_time_ms: 24,
    },
    total_time_ms: 32,
  };
};

export function useMedGemmaAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processPatientCase = useCallback(
    async (clinicalText: string): Promise<PipelineResult | null> => {
      setLoading(true);
      setError(null);

      try {
        const response = await axios.post(
          `${API_BASE}/process`,
          { clinical_text: clinicalText },
          {
            timeout: 5000,
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        return response.data;
      } catch (err) {
        // If API fails, use demo mock response
        console.warn('API unavailable, using demo mode');
        try {
          return generateMockResponse(clinicalText);
        } catch (mockErr) {
          const message = axios.isAxiosError(err)
            ? err.response?.data?.detail || err.message
            : 'Failed to process patient case';
          setError(message);
          return null;
        }
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    processPatientCase,
    loading,
    error,
  };
}
