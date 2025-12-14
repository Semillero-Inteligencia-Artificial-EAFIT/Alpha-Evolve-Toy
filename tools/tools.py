import psutil
import time
import asyncio
import subprocess
import tempfile
import os
import json
import uuid
from datetime import datetime
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

class CodeOptimizer:
    def __init__(self):
        self.tasks = {}
        self.lm_studio_client = AsyncOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    
    def measure_performance(self, code, runs):
        cpu_values = []
        memory_values = []
        time_values = []
        
        for _ in range(runs):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            process = psutil.Process()
            
            cpu_before = process.cpu_percent(interval=0.1)
            mem_before = process.memory_info().rss / 1024 / 1024
            start_time = time.time()
            
            result = subprocess.run(['python3', temp_file], capture_output=True, text=True, timeout=30)
            
            end_time = time.time()
            cpu_after = process.cpu_percent(interval=0.1)
            mem_after = process.memory_info().rss / 1024 / 1024
            
            os.unlink(temp_file)
            
            if result.returncode == 0:
                cpu_values.append(max(cpu_before, cpu_after))
                memory_values.append(mem_after - mem_before)
                time_values.append(end_time - start_time)
            else:
                return None
        
        return {
            'cpu': sum(cpu_values) / len(cpu_values),
            'memory': sum(memory_values) / len(memory_values),
            'time': sum(time_values) / len(time_values),
            'success': True
        }
    
    async def call_lm_studio(self, code, metrics):
        prompt = f"""Optimize this Python code to reduce CPU and memory usage.

Current metrics:
- CPU: {metrics['cpu']:.2f}%
- Memory: {metrics['memory']:.2f} MB
- Time: {metrics['time']:.4f} seconds

Code:
{code}

Return ONLY the optimized Python code without any explanations or markdown formatting."""
        
        completion = await self.lm_studio_client.chat.completions.create(
            model="TheBloke/dolphin-2.2.1-mistral-7B-GGUF",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.1,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    
    async def call_claude(self, code, metrics, api_key):
        prompt = f"""Optimize this Python code to reduce CPU and memory usage.

Current metrics:
- CPU: {metrics['cpu']:.2f}%
- Memory: {metrics['memory']:.2f} MB
- Time: {metrics['time']:.4f} seconds

Code:
{code}

Return ONLY the optimized Python code without any explanations or markdown formatting."""
        
        client = AsyncAnthropic(api_key=api_key)
        
        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    async def optimize(self, code, max_iterations, runs, use_claude, api_key):
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            'status': 'running',
            'history': [],
            'best_code': code,
            'best_metrics': None,
            'current_iteration': 0
        }
        
        asyncio.create_task(self._run_optimization(task_id, code, max_iterations, runs, use_claude, api_key))
        
        return {'task_id': task_id}
    
    async def _run_optimization(self, task_id, code, max_iterations, runs, use_claude, api_key):
        current_code = code
        iteration = 0
        consecutive_no_improvement = 0
        
        initial_metrics = self.measure_performance(current_code, runs)
        
        if not initial_metrics or not initial_metrics['success']:
            self.tasks[task_id]['status'] = 'error'
            self.tasks[task_id]['error'] = 'Initial code failed to execute'
            return
        
        best_code = current_code
        best_metrics = initial_metrics
        
        self.tasks[task_id]['history'].append({
            'iteration': 0,
            'cpu': initial_metrics['cpu'],
            'memory': initial_metrics['memory'],
            'time': initial_metrics['time'],
            'timestamp': datetime.now().isoformat()
        })
        
        while consecutive_no_improvement < max_iterations:
            iteration += 1
            self.tasks[task_id]['current_iteration'] = iteration
            
            if use_claude and api_key:
                optimized_code = await self.call_claude(current_code, best_metrics, api_key)
            else:
                optimized_code = await self.call_lm_studio(current_code, best_metrics)
            
            optimized_code = optimized_code.replace('```python', '').replace('```', '').strip()
            
            new_metrics = self.measure_performance(optimized_code, runs)
            
            if not new_metrics or not new_metrics['success']:
                consecutive_no_improvement += 1
                self.tasks[task_id]['history'].append({
                    'iteration': iteration,
                    'cpu': best_metrics['cpu'],
                    'memory': best_metrics['memory'],
                    'time': best_metrics['time'],
                    'timestamp': datetime.now().isoformat(),
                    'failed': True
                })
                continue
            
            improved = False
            
            if new_metrics['cpu'] < best_metrics['cpu'] or new_metrics['memory'] < best_metrics['memory'] or new_metrics['time'] < best_metrics['time']:
                best_code = optimized_code
                best_metrics = new_metrics
                current_code = optimized_code
                consecutive_no_improvement = 0
                improved = True
            else:
                consecutive_no_improvement += 1
            
            self.tasks[task_id]['history'].append({
                'iteration': iteration,
                'cpu': new_metrics['cpu'],
                'memory': new_metrics['memory'],
                'time': new_metrics['time'],
                'timestamp': datetime.now().isoformat(),
                'improved': improved
            })
            
            await asyncio.sleep(0.1)
        
        self.tasks[task_id]['status'] = 'completed'
        self.tasks[task_id]['best_code'] = best_code
        self.tasks[task_id]['best_metrics'] = best_metrics
    
    def get_task_status(self, task_id):
        if task_id not in self.tasks:
            return {'error': 'Task not found'}
        return self.tasks[task_id]