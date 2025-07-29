#!/usr/bin/env python3
"""
Async Automation Example - BrowserGeist

Demonstrates modern async/await automation patterns:
- Concurrent automation tasks
- High-performance automation workflows
- Connection pooling for efficiency
- Async context managers
- Error handling in async contexts
- Real-world async automation scenarios

This example showcases the power of async automation for
scalable, high-throughput automation workflows.
"""

import asyncio
import sys
import os
import time
from typing import List, Dict, Any

# Add SDK to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'python_sdk'))

from async_browsergeist import AsyncHumanMouse, async_automation_session, MotionProfile, MotionProfiles

async def demo_basic_async_operations():
    """Demonstrate basic async automation operations"""
    print("⚡ Basic Async Operations Demo")
    print("-" * 40)
    
    async with async_automation_session() as bot:
        print("1. Async mouse movements...")
        
        # Execute multiple movements concurrently
        tasks = [
            bot.move_to((300, 200), profile=MotionProfiles.NATURAL),
            bot.move_to((600, 300), profile=MotionProfiles.FAST),
            bot.move_to((400, 500), profile=MotionProfiles.CAREFUL)
        ]
        
        start_time = time.time()
        # Note: These would run sequentially as they affect the same cursor
        # This demonstrates the async API structure
        for task in tasks:
            await task
        duration = time.time() - start_time
        
        print(f"   ⏱️  Completed in {duration:.3f} seconds")
        
        print("2. Async typing operations...")
        
        # Sequential typing operations with async syntax
        await bot.type_text("Async automation with BrowserGeist", delay_profile="natural")
        await bot.type_text("\n")
        await bot.type_text("Modern Python async/await patterns", delay_profile="fast")
        
        print("✅ Basic async operations completed!")

async def demo_concurrent_form_filling():
    """Demonstrate concurrent form processing with connection pooling"""
    print("\n📝 Concurrent Form Filling Demo")
    print("-" * 40)
    
    # Sample form data for multiple forms
    forms_data = [
        {
            "id": "form_1",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "message": "First form submission"
        },
        {
            "id": "form_2", 
            "name": "Bob Smith",
            "email": "bob@example.com",
            "message": "Second form submission"
        },
        {
            "id": "form_3",
            "name": "Carol Williams", 
            "email": "carol@example.com",
            "message": "Third form submission"
        }
    ]
    
    async def fill_single_form(form_data: Dict[str, str], session_id: int):
        """Fill a single form asynchronously"""
        async with async_automation_session(max_connections=5) as bot:
            form_id = form_data["id"]
            print(f"   📋 Processing {form_id} in session {session_id}...")
            
            # Simulate form field positions (different for each form)
            base_x = 300 + (session_id * 50)
            base_y = 200 + (session_id * 30)
            
            # Fill name field
            await bot.move_to((base_x, base_y), profile=MotionProfiles.NATURAL)
            await bot.click()
            await bot.type_text(form_data["name"], delay_profile="fast")
            
            # Fill email field  
            await bot.move_to((base_x, base_y + 50), profile=MotionProfiles.NATURAL)
            await bot.click()
            await bot.type_text(form_data["email"], delay_profile="careful")
            
            # Fill message field
            await bot.move_to((base_x, base_y + 100), profile=MotionProfiles.NATURAL)
            await bot.click()
            await bot.type_text(form_data["message"], delay_profile="natural")
            
            # Submit form
            await bot.move_to((base_x, base_y + 150), profile=MotionProfiles.NATURAL)
            await bot.click()
            
            print(f"   ✅ {form_id} completed")
            return {"form_id": form_id, "status": "completed", "session": session_id}
    
    # Process forms concurrently
    print("Starting concurrent form processing...")
    start_time = time.time()
    
    tasks = [
        fill_single_form(form_data, i) 
        for i, form_data in enumerate(forms_data)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    duration = time.time() - start_time
    
    # Report results
    successful = [r for r in results if isinstance(r, dict)]
    failed = [r for r in results if isinstance(r, Exception)]
    
    print(f"📊 Results: {len(successful)} successful, {len(failed)} failed")
    print(f"⏱️  Total time: {duration:.3f} seconds")
    print("✅ Concurrent form filling completed!")

async def demo_async_error_handling():
    """Demonstrate robust async error handling patterns"""
    print("\n🔧 Async Error Handling Demo") 
    print("-" * 40)
    
    async def risky_automation_task(task_id: int) -> Dict[str, Any]:
        """Simulate an automation task that might fail"""
        try:
            async with async_automation_session(command_timeout=5.0) as bot:
                print(f"   🎯 Starting task {task_id}...")
                
                # Simulate work that might fail
                if task_id == 2:
                    # Simulate timeout error
                    await asyncio.sleep(6.0)  # This will timeout
                elif task_id == 3:
                    # Simulate connection error
                    raise ConnectionError("Simulated connection failure")
                
                # Normal successful work
                await bot.move_to((400 + task_id * 50, 300))
                await bot.click()
                await bot.type_text(f"Task {task_id} completed successfully")
                
                return {"task_id": task_id, "status": "success"}
                
        except asyncio.TimeoutError:
            print(f"   ⏰ Task {task_id} timed out")
            return {"task_id": task_id, "status": "timeout"}
        except ConnectionError as e:
            print(f"   🔌 Task {task_id} connection failed: {e}")
            return {"task_id": task_id, "status": "connection_error"}
        except Exception as e:
            print(f"   ❌ Task {task_id} failed: {e}")
            return {"task_id": task_id, "status": "error", "error": str(e)}
    
    # Run multiple tasks with various failure modes
    tasks = [risky_automation_task(i) for i in range(1, 5)]
    
    results = await asyncio.gather(*tasks, return_exceptions=False)
    
    # Analyze results
    status_counts = {}
    for result in results:
        status = result.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("📊 Task Results:")
    for status, count in status_counts.items():
        print(f"   {status}: {count} tasks")
    
    print("✅ Error handling demo completed!")

async def demo_high_performance_workflow():
    """Demonstrate high-performance automation workflow"""
    print("\n🚀 High-Performance Workflow Demo")
    print("-" * 40)
    
    async def process_data_entry_batch(batch_data: List[Dict[str, str]], batch_id: int):
        """Process a batch of data entry tasks"""
        async with async_automation_session(max_connections=10) as bot:
            print(f"   📦 Processing batch {batch_id} ({len(batch_data)} items)...")
            
            for i, item in enumerate(batch_data):
                # Calculate position for this item
                x = 300 + (i % 3) * 200  # 3 columns
                y = 200 + (i // 3) * 50  # Rows
                
                # Quick data entry
                await bot.move_to((x, y), profile=MotionProfiles.FAST)
                await bot.click()
                await bot.type_text(item["data"], delay_profile="fast")
                
                # Brief pause between items
                await asyncio.sleep(0.1)
            
            return {"batch_id": batch_id, "items_processed": len(batch_data)}
    
    # Generate sample data batches
    batches = []
    for batch_id in range(3):
        batch = [
            {"data": f"Item_{batch_id}_{i}"} 
            for i in range(5)
        ]
        batches.append((batch, batch_id))
    
    print("Starting high-performance data entry workflow...")
    start_time = time.time()
    
    # Process all batches concurrently
    tasks = [process_data_entry_batch(batch, batch_id) for batch, batch_id in batches]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    total_items = sum(r["items_processed"] for r in results)
    
    print(f"📊 Performance Metrics:")
    print(f"   Total items processed: {total_items}")
    print(f"   Total time: {duration:.3f} seconds")
    print(f"   Items per second: {total_items/duration:.2f}")
    print("✅ High-performance workflow completed!")

async def demo_async_captcha_handling():
    """Demonstrate async CAPTCHA handling"""
    print("\n🔐 Async CAPTCHA Handling Demo")
    print("-" * 40)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    async with async_automation_session(
        openai_api_key=openai_key,
        auto_solve_captcha=True
    ) as bot:
        
        print("1. Simulating form submission that triggers CAPTCHA...")
        
        # Move to form submission area
        await bot.move_to((400, 400), profile=MotionProfiles.NATURAL)
        await bot.click()
        
        # Type form data
        await bot.type_text("test@example.com", delay_profile="average")
        
        # Submit form (might trigger CAPTCHA)
        await bot.move_to((400, 500), profile=MotionProfiles.NATURAL)
        await bot.click()
        
        print("2. Checking for CAPTCHA asynchronously...")
        
        # Check for CAPTCHA (this would be async in real implementation)
        # solution = await bot.check_for_captcha_async()
        
        print("   💡 CAPTCHA detection and solving would happen here")
        print("   🤖 OpenAI API solving: Automated")
        print("   🌐 Manual solving: Web interface")
        print("   🔗 2Captcha service: Outsourced")
        
        print("✅ Async CAPTCHA handling demo completed!")

async def demo_session_management():
    """Demonstrate advanced async session management"""
    print("\n🎛️  Advanced Session Management Demo")
    print("-" * 40)
    
    class AsyncAutomationManager:
        """Manager for complex automation sessions"""
        
        def __init__(self, max_concurrent_sessions: int = 5):
            self.max_concurrent_sessions = max_concurrent_sessions
            self.active_sessions = []
            self.session_pool = asyncio.Queue(maxsize=max_concurrent_sessions)
        
        async def __aenter__(self):
            # Pre-populate session pool
            for i in range(self.max_concurrent_sessions):
                session = AsyncHumanMouse()
                await self.session_pool.put(session)
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            # Clean up all sessions
            while not self.session_pool.empty():
                session = await self.session_pool.get()
                await session.close()
        
        async def execute_task(self, task_func, *args, **kwargs):
            """Execute a task using a session from the pool"""
            session = await self.session_pool.get()
            try:
                result = await task_func(session, *args, **kwargs)
                return result
            finally:
                await self.session_pool.put(session)
    
    async def automation_task(session: AsyncHumanMouse, task_id: int):
        """Sample automation task"""
        await session.move_to((300 + task_id * 100, 300))
        await session.click()
        await session.type_text(f"Task {task_id} data")
        return {"task_id": task_id, "status": "completed"}
    
    # Use the session manager
    async with AsyncAutomationManager(max_concurrent_sessions=3) as manager:
        print("Executing tasks with session pool management...")
        
        tasks = [
            manager.execute_task(automation_task, i)
            for i in range(8)  # More tasks than sessions
        ]
        
        results = await asyncio.gather(*tasks)
        
        successful_tasks = len([r for r in results if r.get("status") == "completed"])
        print(f"📊 Completed {successful_tasks}/{len(tasks)} tasks")
    
    print("✅ Session management demo completed!")

async def main():
    """Run all async automation demonstrations"""
    print("⚡ BrowserGeist - Async Automation Examples")
    print("=" * 60)
    print()
    print("This demo showcases modern async/await automation capabilities:")
    print("• Concurrent automation task execution")
    print("• High-performance workflows with connection pooling")
    print("• Robust async error handling patterns")
    print("• Advanced session management strategies")
    print("• Async CAPTCHA handling integration")
    print("• Scalable automation architectures")
    print()
    
    try:
        await demo_basic_async_operations()
        await demo_concurrent_form_filling()
        await demo_async_error_handling()
        await demo_high_performance_workflow()
        await demo_async_captcha_handling()
        await demo_session_management()
        
        print("\n🎉 All async automation demos completed successfully!")
        print("\n⚡ Key Async Features Demonstrated:")
        print("   • async/await syntax for modern Python patterns")
        print("   • Connection pooling for high-throughput scenarios")
        print("   • Concurrent task execution with asyncio.gather()")
        print("   • Robust error handling in async contexts")
        print("   • Session lifecycle management")
        print("   • Performance optimization techniques")
        
        print("\n🏗️  Architecture Benefits:")
        print("   • Scalable to hundreds of concurrent operations")
        print("   • Efficient resource utilization")
        print("   • Non-blocking I/O for better performance")
        print("   • Modern Python async ecosystem integration")
        print("   • Production-ready for enterprise automation")
        
        print("\n💡 Best Practices:")
        print("   • Use connection pooling for multiple automation tasks")
        print("   • Implement proper error handling and retry logic")
        print("   • Leverage asyncio.gather() for concurrent operations")
        print("   • Manage session lifecycles with async context managers")
        print("   • Monitor performance metrics for optimization")
        
    except ConnectionError:
        print("❌ Connection failed: BrowserGeist daemon not running")
        print("\n🔧 To fix this:")
        print("   1. Start the daemon: ./bin/browsergeist daemon start")
        print("   2. Check permissions: ./bin/browsergeist doctor")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("Run './bin/browsergeist doctor' to diagnose issues")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
