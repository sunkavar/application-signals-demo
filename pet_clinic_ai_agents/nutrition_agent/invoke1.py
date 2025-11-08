#!/usr/bin/env python3
import boto3
import json
import uuid
import sys
from datetime import datetime

class BedrockAgentCLI:
    def __init__(self):
        self.client = boto3.client('bedrock-agentcore', region_name='us-west-2')
        self.agent_arn = 'arn:aws:bedrock-agentcore:us-west-2:203918868918:runtime/nutrition_agent-taW4LXE6Yz'
        self.session_id = self.generate_session_id()
        self.qualifier = "DEFAULT"
        
    def generate_session_id(self):
        """Generate a unique session ID that's 33+ characters"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4()).replace('-', '')
        return f"nutrition_agent_{unique_id}"
    
    def invoke_agent(self, prompt):
        """Send a prompt to the Bedrock agent and return the response"""
        try:
            payload = json.dumps({"prompt": prompt})
            
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_arn,
                runtimeSessionId=self.session_id,
                payload=payload,
                qualifier=self.qualifier
            )
            
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            return response_data
            
        except Exception as e:
            return {"error": f"Failed to invoke agent: {str(e)}"}
    
    def print_response(self, response_data):
        """Pretty print the agent response"""
        print("\n" + "="*60)
        print("🤖 AGENT RESPONSE")
        print("="*60)
        
        if "error" in response_data:
            print(f"❌ Error: {response_data['error']}")
        else:
            # Handle different response formats
            if isinstance(response_data, dict):
                if 'content' in response_data:
                    print(response_data['content'])
                elif 'message' in response_data:
                    print(response_data['message'])
                else:
                    print(json.dumps(response_data, indent=2))
            else:
                print(response_data)
        
        print("="*60 + "\n")
    
    def run_interactive(self):
        """Run the interactive CLI"""
        print("🍎 Nutrition Agent CLI")
        print("=" * 40)
        print(f"Session ID: {self.session_id}")
        print("Type 'quit', 'exit', or 'q' to end the session")
        print("Type 'help' for available commands")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'session':
                    print(f"Current session ID: {self.session_id}")
                    continue
                elif user_input.lower() == 'new-session':
                    self.session_id = self.generate_session_id()
                    print(f"New session started: {self.session_id}")
                    continue
                
                # Send prompt to agent
                print("🔄 Thinking...")
                response = self.invoke_agent(user_input)
                self.print_response(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
    
    def show_help(self):
        """Show available commands"""
        print("\n📋 Available Commands:")
        print("  help        - Show this help message")
        print("  session     - Show current session ID")
        print("  new-session - Start a new session")
        print("  quit/exit/q - Exit the CLI")
        print("\n💡 Just type your question to chat with the nutrition agent!")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Non-interactive mode - single prompt
        cli = BedrockAgentCLI()
        prompt = " ".join(sys.argv[1:])
        print(f"Prompt: {prompt}")
        response = cli.invoke_agent(prompt)
        cli.print_response(response)
    else:
        # Interactive mode
        cli = BedrockAgentCLI()
        cli.run_interactive()

if __name__ == "__main__":
    main()