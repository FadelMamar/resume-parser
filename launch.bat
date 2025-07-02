call cd "D:\workspace\repos\resume-parser"

call .venv\Scripts\activate

@REM load env variables from .env file

call load_env.bat

call streamlit run ui.py --server.port 8500

@REM start D:\workspace\llama-cpp\llama-server.exe -hf ggml-org/Qwen2.5-VL-3B-Instruct-GGUF:q4_k_m ^
@REM     --port 8001 --ctx-size 20000

@REM start D:\workspace\llama-cpp\llama-server.exe -hf ggml-org/Qwen3-1.7B-GGUF:q4_k_m ^
@REM     --port 8002 --ctx-size 20000