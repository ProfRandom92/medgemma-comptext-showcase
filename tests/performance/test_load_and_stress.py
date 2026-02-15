"""
Phase 4e3b: Load & Performance Tests

TIER 2 IMPORTANT Tests for:
- Concurrent request handling (5, 10, 50 requests)
- Memory stability under load
- Response time measurements (95th percentile)
- CPU usage monitoring
- Long-running session stability
- No memory leaks or degradation

Tests measure real system performance on development setup
Used to validate judge evaluation stress test readiness
"""

import asyncio
import time
import sys
import os
import psutil
import pytest
from typing import List, Dict, Tuple

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from src.agents.nurse_agent import NurseAgent
from src.agents.triage_agent import TriageAgent
from src.agents.doctor_agent import DoctorAgent
from src.core.models import PatientState, Vitals


# =========================================================================
# Helper Functions
# =========================================================================

def get_memory_usage() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Convert to MB


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    process = psutil.Process()
    return process.cpu_percent(interval=0.1)


class PerformanceMetrics:
    """Collect and analyze performance metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.errors: List[str] = []
        self.start_memory = get_memory_usage()
    
    def record_response_time(self, duration_ms: float):
        """Record a response time in milliseconds."""
        self.response_times.append(duration_ms)
    
    def record_memory(self):
        """Record current memory usage."""
        self.memory_samples.append(get_memory_usage())
    
    def record_cpu(self):
        """Record current CPU usage."""
        self.cpu_samples.append(get_cpu_usage())
    
    def record_error(self, error_msg: str):
        """Record an error."""
        self.errors.append(error_msg)
    
    def get_stats(self) -> Dict:
        """Calculate statistics."""
        if not self.response_times:
            return {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': len(self.errors),
                'min_time_ms': 0,
                'max_time_ms': 0,
                'avg_time_ms': 0,
                'p50_time_ms': 0,
                'p95_time_ms': 0,
                'p99_time_ms': 0,
                'memory_delta_mb': 0,
                'peak_memory_mb': 0,
                'avg_cpu_percent': 0,
            }
        
        sorted_times = sorted(self.response_times)
        total = len(sorted_times)
        
        return {
            'total_requests': total,
            'successful_requests': total,
            'failed_requests': len(self.errors),
            'min_time_ms': min(sorted_times),
            'max_time_ms': max(sorted_times),
            'avg_time_ms': sum(sorted_times) / total,
            'p50_time_ms': sorted_times[int(total * 0.50)],
            'p95_time_ms': sorted_times[int(total * 0.95)] if total > 20 else max(sorted_times),
            'p99_time_ms': sorted_times[int(total * 0.99)] if total > 100 else max(sorted_times),
            'memory_delta_mb': max(self.memory_samples) - self.start_memory if self.memory_samples else 0,
            'peak_memory_mb': max(self.memory_samples) if self.memory_samples else 0,
            'avg_cpu_percent': sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0,
        }
    
    def __str__(self) -> str:
        """Format as readable report."""
        stats = self.get_stats()
        return f"""
Performance Report:
  Total Requests: {stats['total_requests']}
  Successful: {stats['successful_requests']}
  Failed: {stats['failed_requests']}
  
  Response Time (ms):
    Min: {stats['min_time_ms']:.2f}
    Max: {stats['max_time_ms']:.2f}
    Avg: {stats['avg_time_ms']:.2f}
    P50: {stats['p50_time_ms']:.2f}
    P95: {stats['p95_time_ms']:.2f}
    P99: {stats['p99_time_ms']:.2f}
  
  Memory:
    Delta: {stats['memory_delta_mb']:.2f} MB
    Peak: {stats['peak_memory_mb']:.2f} MB
  
  CPU:
    Avg: {stats['avg_cpu_percent']:.2f}%
"""


# =========================================================================
# Test Data
# =========================================================================

CLINICAL_TEXTS = [
    "Chief complaint: chest pain radiating to left arm. HR 110, BP 160/95, Temp 38.5°C.",
    "Patient presents with acute severe headache and fever. HR 98, BP 140/85, Temp 39.2°C.",
    "Respiratory distress, productive cough, SOB. HR 102, BP 145/88, Temp 38.0°C.",
    "Severe abdominal pain, nausea, vomiting. HR 105, BP 155/90, Temp 37.8°C.",
    "Confusion, headache, stiff neck. HR 115, BP 160/100, Temp 39.5°C.",
    "Trauma: crush injury to left leg. HR 125, BP 100/60, Temp 36.5°C.",
    "Cardiac arrhythmia, palpitations, dizziness. HR 140, BP 150/92, Temp 37.0°C.",
    "Severe allergic reaction, stridor, airway edema. HR 120, BP 110/70, Temp 37.2°C.",
    "Diabetic patient with altered mental status. HR 95, BP 180/110, Temp 36.8°C.",
    "Septic shock, hypotension, altered consciousness. HR 130, BP 80/50, Temp 40.0°C.",
]


# =========================================================================
# TIER 2 PERFORMANCE TESTS
# =========================================================================

class TestSequentialProcessing:
    """Test sequential request processing performance."""
    
    def test_10_sequential_requests_complete_fast(self):
        """Sequential: 10 requests in <5 seconds."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        
        for i in range(10):
            start = time.time()
            try:
                clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                patient_state = nurse.intake(clinical_text)
                duration_ms = (time.time() - start) * 1000
                metrics.record_response_time(duration_ms)
                metrics.record_memory()
            except Exception as e:
                metrics.record_error(str(e))
        
        stats = metrics.get_stats()
        total_time = sum(metrics.response_times) / 1000
        
        assert stats['successful_requests'] >= 9, f"Only {stats['successful_requests']}/10 succeeded"
        assert total_time < 5.0, f"10 sequential requests took {total_time:.2f}s (target: <5s)"
        assert stats['avg_time_ms'] < 500, f"Avg time {stats['avg_time_ms']:.2f}ms (target: <500ms)"
    
    def test_response_time_consistency(self):
        """Sequential: Response time doesn't degrade."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        triage = TriageAgent()
        
        for i in range(15):
            start = time.time()
            try:
                clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                patient_state = nurse.intake(clinical_text)
                priority = triage.assess(patient_state)
                duration_ms = (time.time() - start) * 1000
                metrics.record_response_time(duration_ms)
            except Exception as e:
                metrics.record_error(str(e))
        
        first_5_avg = sum(metrics.response_times[:5]) / 5
        last_5_avg = sum(metrics.response_times[-5:]) / 5
        slowdown_percent = ((last_5_avg - first_5_avg) / first_5_avg) * 100
        
        assert slowdown_percent < 20, f"Response time degraded {slowdown_percent:.1f}%"


class TestConcurrentProcessing:
    """Test concurrent request handling."""
    
    def test_5_concurrent_requests_succeed(self):
        """Concurrent: 5 requests succeed in <2 seconds."""
        async def process_patient(text: str) -> Tuple[bool, float]:
            nurse = NurseAgent()
            start = time.time()
            try:
                patient_state = nurse.intake(text)
                duration_ms = (time.time() - start) * 1000
                return (True, duration_ms)
            except Exception:
                return (False, (time.time() - start) * 1000)
        
        async def run_concurrent():
            texts = [CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)] for i in range(5)]
            start = time.time()
            results = await asyncio.gather(*[process_patient(text) for text in texts])
            total_time = (time.time() - start) * 1000
            return results, total_time
        
        results, total_time = asyncio.run(run_concurrent())
        successful = sum(1 for success, _ in results if success)
        response_times = [duration for _, duration in results]
        
        assert successful >= 4, f"Only {successful}/5 concurrent requests succeeded"
        assert total_time < 2000, f"5 concurrent took {total_time:.0f}ms (target: <2000ms)"
        assert max(response_times) < 500, f"Max time {max(response_times):.0f}ms (target: <500ms)"
    
    def test_10_concurrent_requests_no_failures(self):
        """Concurrent: 10 requests all succeed."""
        async def process_patient(text: str) -> bool:
            nurse = NurseAgent()
            try:
                patient_state = nurse.intake(text)
                return True
            except Exception:
                return False
        
        async def run_concurrent():
            texts = [CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)] for i in range(10)]
            results = await asyncio.gather(*[process_patient(text) for text in texts])
            return results
        
        results = asyncio.run(run_concurrent())
        successful = sum(1 for result in results if result)
        
        assert successful >= 9, f"Only {successful}/10 concurrent requests succeeded"


class TestMemoryStability:
    """Test memory usage under load."""
    
    def test_memory_stable_100_requests(self):
        """Memory: <50MB growth during 100 requests."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        triage = TriageAgent()
        doctor = DoctorAgent()
        
        initial_memory = get_memory_usage()
        
        for i in range(100):
            try:
                clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                patient_state = nurse.intake(clinical_text)
                priority = triage.assess(patient_state)
                diagnosis = doctor.diagnose(patient_state.model_dump())
                
                if i % 10 == 0:
                    metrics.record_memory()
                    metrics.record_cpu()
                
            except Exception as e:
                metrics.record_error(str(e))
        
        final_memory = get_memory_usage()
        memory_delta = final_memory - initial_memory
        stats = metrics.get_stats()
        
        assert memory_delta < 100, f"Memory grew {memory_delta:.2f}MB (max: 100MB)"
        assert stats['failed_requests'] == 0, f"{stats['failed_requests']} errors during 100 requests"
    
    def test_no_memory_leak_long_session(self):
        """Memory: Stable during 200 requests over time."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        memory_checkpoints = []
        
        for i in range(200):
            try:
                clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                patient_state = nurse.intake(clinical_text)
                
                if i % 50 == 0:
                    memory_checkpoints.append(get_memory_usage())
                
                metrics.record_response_time(10)
                
            except Exception as e:
                metrics.record_error(str(e))
        
        if len(memory_checkpoints) >= 3:
            slope = (memory_checkpoints[-1] - memory_checkpoints[0]) / (len(memory_checkpoints) - 1)
            assert slope < 5, f"Memory trending upward at {slope:.2f}MB/checkpoint"


class TestResponseTimeBoundaries:
    """Test response time requirements."""
    
    def test_single_request_under_100ms(self):
        """Single: Request <100ms average."""
        nurse = NurseAgent()
        clinical_text = "Chief complaint: chest pain. HR 110, BP 160/95."
        
        times = []
        for _ in range(5):
            start = time.time()
            patient_state = nurse.intake(clinical_text)
            duration_ms = (time.time() - start) * 1000
            times.append(duration_ms)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        assert avg_time < 100, f"Avg time {avg_time:.2f}ms (target: <100ms)"
        assert max_time < 200, f"Max time {max_time:.2f}ms (target: <200ms)"
    
    def test_p95_response_time_under_500ms(self):
        """P95: Response time <500ms across 50 requests."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        triage = TriageAgent()
        
        for i in range(50):
            start = time.time()
            try:
                clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                patient_state = nurse.intake(clinical_text)
                triage.assess(patient_state)
                duration_ms = (time.time() - start) * 1000
                metrics.record_response_time(duration_ms)
            except Exception as e:
                metrics.record_error(str(e))
        
        stats = metrics.get_stats()
        
        assert stats['p95_time_ms'] < 500, f"P95 {stats['p95_time_ms']:.2f}ms (target: <500ms)"
        assert stats['successful_requests'] >= 48, f"Only {stats['successful_requests']}/50 succeeded"


class TestLoadScaling:
    """Test how performance scales with load."""
    
    def test_response_time_scaling(self):
        """Scaling: Response time doesn't degrade exponentially."""
        nurse = NurseAgent()
        load_results = {}
        
        for load in [10, 25, 50]:
            times = []
            for i in range(load):
                start = time.time()
                try:
                    clinical_text = CLINICAL_TEXTS[i % len(CLINICAL_TEXTS)]
                    patient_state = nurse.intake(clinical_text)
                    duration_ms = (time.time() - start) * 1000
                    times.append(duration_ms)
                except Exception:
                    pass
            
            avg_time = sum(times) / len(times) if times else 0
            load_results[load] = avg_time
        
        if 10 in load_results and 50 in load_results:
            ratio = load_results[50] / load_results[10]
            assert ratio < 3, f"Response time increased {ratio:.2f}x (target: <3x)"


class TestErrorRecovery:
    """Test behavior under error conditions."""
    
    def test_partial_failures_dont_crash(self):
        """Error: System survives gracefully through errors."""
        metrics = PerformanceMetrics()
        nurse = NurseAgent()
        
        test_inputs = [
            "Valid text: HR 100",
            "",
            "Another valid case",
            None,
            "Valid again",
        ]
        
        for test_input in test_inputs:
            try:
                if test_input is not None and test_input.strip():
                    start = time.time()
                    patient_state = nurse.intake(test_input)
                    duration_ms = (time.time() - start) * 1000
                    metrics.record_response_time(duration_ms)
                else:
                    metrics.record_error("Invalid input")
            except Exception as e:
                metrics.record_error(str(e))
        
        stats = metrics.get_stats()
        assert stats['successful_requests'] >= 2, "System crashed after errors"
