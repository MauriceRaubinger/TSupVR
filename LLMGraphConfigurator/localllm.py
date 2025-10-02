import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import gc
import psutil
import GPUtil
import ctypes
import sys

'''def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if is_admin():
    print("Running as admin!")
    # Your code here
else:
    print("Re-launching as admin...")
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1
    )
'''



def check_gpu_memory():
    """Check available GPU memory"""
    if torch.cuda.is_available():
        gpu = GPUtil.getGPUs()[0]
        print(f"GPU: {gpu.name}")
        print(f"GPU Memory: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB ({gpu.memoryUtil * 100:.1f}% used)")
        print(f"GPU Free Memory: {gpu.memoryFree}MB")
    else:
        print("CUDA not available")


def clear_memory():
    """Clear GPU and system memory"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


class LocalLLM:
    def __init__(self, model_name="distilgpt2"):
        """
        Initialize the local LLM

        Recommended models for RTX 3060 (12GB VRAM):
        - "distilgpt2" (Very lightweight, good for testing)
        - "gpt2" (Original GPT-2)
        - "microsoft/DialoGPT-medium" (Small, good for chat)
        - "microsoft/DialoGPT-large" (Medium size)
        - "EleutherAI/gpt-neo-1.3B" (1.3B parameters)
        - "EleutherAI/gpt-neo-2.7B" (2.7B parameters, may be tight on memory)
        """
        self.model_name = model_name

        # Check CUDA availability with better error handling
        if torch.cuda.is_available():
            try:
                # Test CUDA functionality
                torch.cuda.init()
                self.device = "cuda"
                print(f"CUDA is available! Using GPU: {torch.cuda.get_device_name()}")
            except Exception as e:
                print(f"CUDA available but not working properly: {e}")
                print("Falling back to CPU")
                self.device = "cpu"
        else:
            print("CUDA not available, using CPU")
            self.device = "cpu"

        print(f"Using device: {self.device}")

        # Check memory before loading (only if GPU available)
        if self.device == "cuda":
            check_gpu_memory()

        try:
            print(f"Loading model: {model_name}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model with memory optimization
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,  # Use half precision to save memory
                    device_map="auto",  # Automatically distribute across available GPUs
                    low_cpu_mem_usage=True  # Reduce CPU memory usage during loading
                )
            else:
                # CPU version - don't use float16 or device_map
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    low_cpu_mem_usage=True
                )
                self.model.to(self.device)

            print("Model loaded successfully!")
            if self.device == "cuda":
                check_gpu_memory()

        except Exception as e:
            print(f"Error loading model: {e}")
            print("Try a smaller model or ensure you have enough GPU memory")
            raise

    def generate_text(self, prompt, max_length=100, temperature=0.7, top_p=0.9, do_sample=True):
        """Generate text from a prompt"""
        try:
            # Encode the input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    attention_mask=torch.ones_like(inputs)
                )

            # Decode the output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Return only the new generated part
            return generated_text[len(prompt):].strip()

        except Exception as e:
            print(f"Error during generation: {e}")
            return None

    def chat(self):
        """Interactive chat mode"""
        print("\n=== Local LLM Chat ===")
        print("Type 'quit' to exit, 'clear' to clear memory")
        print("Type 'memory' to check GPU memory usage\n")

        conversation_history = ""

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'clear':
                clear_memory()
                conversation_history = ""
                print("Memory cleared!")
                continue
            elif user_input.lower() == 'memory':
                check_gpu_memory()
                continue

            # Build prompt with conversation history
            if conversation_history:
                prompt = f"{conversation_history}\nYou: {user_input}\nBot:"
            else:
                prompt = f"You: {user_input}\nBot:"

            # Generate response
            response = self.generate_text(prompt, max_length=len(prompt.split()) + 50)

            if response:
                print(f"Bot: {response}")
                conversation_history = prompt + " " + response

                # Trim conversation history if it gets too long
                if len(conversation_history.split()) > 200:
                    conversation_history = " ".join(conversation_history.split()[-150:])
            else:
                print("Bot: Sorry, I couldn't generate a response.")


def main():
    """Main function to run the LLM"""

    # Check if CUDA is available
    if not torch.cuda.is_available():
        print("CUDA is not available. Make sure you have:")
        print("1. NVIDIA drivers installed")
        print("2. PyTorch with CUDA support installed")
        return

    print("Available models for RTX 3060:")
    models = [
        "distilgpt2",  # Very lightweight
        "gpt2",  # Small
        "microsoft/DialoGPT-medium",  # Good for chat
        "EleutherAI/gpt-neo-1.3B",  # Larger, more capable
        "microsoft/DialoGPT-large",  # Large chat model
        "microsoft/phi-2"
    ]

    for i, model in enumerate(models, 1):
        print(f"{i}. {model}")

    # Let user choose model
    selected_model=models[5]
    try:
        # Initialize the LLM
        llm = LocalLLM(selected_model)

        # Start interactive chat
        #llm.chat()
        print(llm.generate_text("Hello how are you?"))

    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure you have enough GPU memory")
        print("2. Try a smaller model")
        print("3. Close other applications using GPU")
        print("4. Restart your Python environment")

    finally:
        pass
        # Clean up
        #lear_memory()


if __name__ == "__main__":
    main()