from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QComboBox, QLineEdit, QTextBrowser, QTreeView,
    QLabel, QSplitter, QFileSystemModel
)
from PySide6.QtCore import Qt, QDir, QTimer
import sys
import os
from pathlib import Path
from typing import Dict, Type
import markdown2
from PySide6.QtGui import QTextCursor

from whittle.src.entities.llm_agent import LLMAgent
from whittle.src.entities.cfd_software import CFDSoftware
from whittle.src.application.llm_agent_interactor import OpenAILLMAgent, ClaudeLLMAgent
from whittle.src.application.cfd_interactor import FOAM, SU2

class LLMAgentFactory:
    """Factory for creating LLM agents"""
    _agents: Dict[str, Type[LLMAgent]] = {
        "GPT-4.1": OpenAILLMAgent,
        "Claude": ClaudeLLMAgent
    }

    @classmethod
    def create(cls, agent_type: str, system_prompt: str) -> LLMAgent:
        agent_class = cls._agents.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown LLM agent type: {agent_type}")
        return agent_class(system_prompt)

class CFDSoftwareFactory:
    """Factory for creating CFD software instances"""
    _software: Dict[str, Type[CFDSoftware]] = {
        "OpenFOAM": FOAM,
        "SU2": SU2
    }

    @classmethod
    def create(cls, software_type: str, case_dir: Path) -> CFDSoftware:
        software_class = cls._software.get(software_type)
        if not software_class:
            raise ValueError(f"Unknown CFD software type: {software_type}")
        return software_class(case_dir)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whittle")
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create left panel for file browser
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Set up file system model and view
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.currentPath())
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.currentPath()))
        left_layout.addWidget(self.tree_view)
        
        layout.addWidget(left_panel)
        
        # Create right panel for chat
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add dropdowns for CFD software and LLM selection
        dropdown_layout = QHBoxLayout()
        
        self.cfd_dropdown = QComboBox()
        self.cfd_dropdown.addItems(["OpenFOAM", "SU2"])
        dropdown_layout.addWidget(self.cfd_dropdown)
        
        self.llm_dropdown = QComboBox()
        self.llm_dropdown.addItems(["Claude", "GPT-4.1"])
        dropdown_layout.addWidget(self.llm_dropdown)
        
        right_layout.addLayout(dropdown_layout)
        
        # Add chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setMarkdown("")  # Initialize empty
        right_layout.addWidget(self.chat_display)
        
        # Add message input and send button
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        right_layout.addLayout(input_layout)
        
        layout.addWidget(right_panel)
        
        # Initialize LLM agent as None
        self.llm_agent = None
        
        # Set size of the window
        self.resize(1200, 800)
        
    def append_markdown_message(self, role: str | None, content: str, is_error: bool = False):
        """Append a message to the chat display"""
        if role:
            self.chat_display.append(f"\n**{role}**: ")
        
        if is_error:
            self.chat_display.append(f"*Error: {content}*")
        else:
            self.chat_display.append(content)
            
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Handle sending a message to the LLM agent"""
        if not self.llm_agent:
            self.append_markdown_message("Error", "No LLM agent selected", is_error=True)
            return
            
        message = self.message_input.text()
        if message:
            # Clear the input and disable the send button
            self.message_input.clear()
            self.send_btn.setEnabled(False)
            
            self.append_markdown_message("You", message)
            self.append_markdown_message(None, "\n")
            
            try:
                # Get complete response
                response = self.llm_agent.return_response(message)
                
                # Start with Assistant: header
                self.append_markdown_message("Assistant", "")
                
                # Accumulate the complete response
                full_response = ""
                
                # Stream the response
                for event in response:
                    if hasattr(event.choices[0].delta, 'content'):
                        content = event.choices[0].delta.content
                        if content is not None:
                            full_response += content
                            # Convert markdown to HTML and display
                            try:
                                html = markdown2.markdown(full_response, extras=['fenced-code-blocks', 'tables'])
                                self.chat_display.setHtml(html)
                            except:
                                # If markdown conversion fails, show plain text
                                self.chat_display.setPlainText(full_response)
                            QApplication.processEvents()
                
                self.append_markdown_message(None, "\n")
                
            except Exception as e:
                self.append_markdown_message("Error", str(e), is_error=True)
            
            # Re-enable the send button
            self.send_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
