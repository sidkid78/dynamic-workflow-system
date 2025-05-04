# build5/backend/app/cli.py
import argparse
import os
import sys
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Build5 MCP CLI tools")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Dev command
    dev_parser = subparsers.add_parser("dev", help="Run MCP server in development mode")
    dev_parser.add_argument("--fs", action="store_true", help="Run file system server")
    dev_parser.add_argument("--rag", action="store_true", help="Run RAG server")
    dev_parser.add_argument("--combined", action="store_true", help="Run combined server")
    dev_parser.add_argument("--with", dest="with_packages", action="append", default=[], help="Additional packages")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install MCP server in Claude Desktop")
    install_parser.add_argument("--fs", action="store_true", help="Install file system server")
    install_parser.add_argument("--rag", action="store_true", help="Install RAG server")
    install_parser.add_argument("--combined", action="store_true", help="Install combined server")
    install_parser.add_argument("--name", type=str, help="Server name in Claude Desktop")
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(script_dir))  # build5/backend
    
    # Set default server type if none specified
    if args.command in ["dev", "install"] and not any([args.fs, args.rag, args.combined]):
        args.combined = True
    
    if args.command == "dev":
        server_path = None
        if args.fs:
            server_path = os.path.join(script_dir, "mcp", "file_system_server.py")
        elif args.rag:
            server_path = os.path.join(script_dir, "mcp", "rag_server.py")
        elif args.combined:
            server_path = os.path.join(script_dir, "mcp", "combined_server.py")
        
        cmd = ["mcp", "dev", server_path]
        for pkg in args.with_packages:
            cmd.extend(["--with", pkg])
        
        subprocess.run(cmd)
    
    elif args.command == "install":
        server_path = None
        server_name = args.name or "Build5"
        
        if args.fs:
            server_path = os.path.join(script_dir, "mcp", "file_system_server.py")
            server_name = args.name or "Build5-FileSystem"
        elif args.rag:
            server_path = os.path.join(script_dir, "mcp", "rag_server.py")
            server_name = args.name or "Build5-RAG"
        elif args.combined:
            server_path = os.path.join(script_dir, "mcp", "combined_server.py")
            server_name = args.name or "Build5-Combined"
        
        cmd = ["mcp", "install", server_path, "--name", server_name]
        subprocess.run(cmd)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()