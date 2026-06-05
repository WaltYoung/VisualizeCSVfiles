import os
import sys

os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

from streamlit.web.cli import main as streamlit_main


if __name__ == "__main__":
    # 模拟命令行参数：streamlit run main.py
    sys.argv = ["streamlit", "run", "main.py"] + sys.argv[1:]
    sys.exit(streamlit_main())