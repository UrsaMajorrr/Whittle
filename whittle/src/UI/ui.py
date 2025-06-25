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

class WhittleMainWindow(QMainWindow):
    def __init__(self):
        super.__init__()
        self.setWindowTitle("Whittle - CFD AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize attributes
        self.llm_agent = None
        self.cfd_software = None
        
        # Create the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left panel (file structure)
        left_panel = self.create_file_panel()
        
        # Create right panel (controls and chat)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add controls section
        controls_widget = self.create_controls()
        right_layout.addWidget(controls_widget)
        
        # Add chat section
        chat_widget = self.create_chat_widget()
        right_layout.addWidget(chat_widget, stretch=1)
        
        # Add panels to splitter for resizing
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
    
    def create_file_panel(self):
        """Create the file structure panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Label
        layout.addWidget(QLabel("Project Files"))
        
        # File system model and view
        model = QFileSystemModel()
        model.setRootPath(str(Path.cwd()))
        
        tree = QTreeView()
        tree.setModel(model)
        tree.setRootIndex(model.index(str(Path.cwd())))
        tree.setColumnWidth(0, 250)
        tree.hideColumn(1)  # Size column
        tree.hideColumn(2)  # Type column
        tree.hideColumn(3)  # Date modified column
        
        layout.addWidget(tree)
        return panel
    
    def create_controls(self):
        """Create the controls section"""
        controls = QWidget()
        layout = QVBoxLayout(controls)
        
        # CFD Software dropdown
        cfd_layout = QHBoxLayout()
        cfd_layout.addWidget(QLabel("CFD Software:"))
        self.cfd_dropdown = QComboBox()
        self.cfd_dropdown.addItems(list(CFDSoftwareFactory._software.keys()))
        self.cfd_dropdown.currentTextChanged.connect(self.on_cfd_software_changed)
        cfd_layout.addWidget(self.cfd_dropdown)
        layout.addLayout(cfd_layout)
        
        # LLM Model dropdown
        llm_layout = QHBoxLayout()
        llm_layout.addWidget(QLabel("LLM Model:"))
        self.llm_dropdown = QComboBox()
        self.llm_dropdown.addItem("None")
        self.llm_dropdown.addItems(list(LLMAgentFactory._agents.keys()))
        self.llm_dropdown.currentTextChanged.connect(self.on_llm_agent_changed)
        llm_layout.addWidget(self.llm_dropdown)
        layout.addLayout(llm_layout)
        
        # Command input
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(QLabel("Command:"))
        self.cmd_input = QLineEdit()
        cmd_layout.addWidget(self.cmd_input)
        layout.addLayout(cmd_layout)
        
        # Execute button
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_command)
        self.execute_btn.setEnabled(False)  # Enable when CFD software is selected
        layout.addWidget(self.execute_btn)
        
        return controls
    
    def create_chat_widget(self):
        """Create the chat history widget"""
        chat_widget = QWidget()
        layout = QVBoxLayout(chat_widget)
        
        # Chat history
        layout.addWidget(QLabel("Chat History"))
        self.chat_history = QTextBrowser()
        self.chat_history.setOpenExternalLinks(True)  # Allow clicking links
        layout.addWidget(self.chat_history)
        
        # Message input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)  # Enable when LLM is selected
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        return chat_widget

    def append_markdown_message(self, prefix: str | None, content: str | None, is_error: bool = False):
        """Append a message to chat history with markdown support"""
        # Handle None content
        if content is None:
            return
            
        # Convert markdown to HTML
        if is_error:
            html_content = f'<p style="color: red;">{prefix}: {content}</p>'
        else:
            try:
                if content == "\n":
                    html_content = '<br>'
                elif prefix is not None:
                    html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
                    html_content = f'<p><strong>{prefix}:</strong></p>{html_content}'
                else:
                    # For content without prefix, just preserve spaces
                    content = content.replace(" ", "&nbsp;")
                    html_content = f'<span>{content}</span>'
            except Exception as e:
                html_content = f'<p>{prefix}: {e}</p>'
        
        # Move cursor to end and insert HTML
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.insertHtml(html_content)
        
        # Scroll to the new content
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def on_cfd_software_changed(self, software_name: str):
        """Handle CFD software selection"""
        try:
            self.cfd_software = CFDSoftwareFactory.create(software_name, Path.cwd())
            self.execute_btn.setEnabled(True)
            self.append_markdown_message("System", f"Selected CFD software: **{software_name}**")
        except Exception as e:
            self.append_markdown_message("Error", str(e), is_error=True)
    
    def on_llm_agent_changed(self, agent_name: str):
        """Handle LLM agent selection"""
        if agent_name == "None":
            self.llm_agent = None
            self.send_btn.setEnabled(False)
            return
            
        try:
            system_prompt = "You are a helpful CFD assistant"
            self.llm_agent = LLMAgentFactory.create(agent_name, system_prompt)
            self.send_btn.setEnabled(True)
            self.append_markdown_message("System", f"Selected LLM agent: **{agent_name}**")
        except ValueError as e:
            self.append_markdown_message("Error", f"API key error: {str(e)}\nPlease ensure you have set the appropriate environment variable.", is_error=True)
            self.llm_dropdown.setCurrentText("None")
        except Exception as e:
            self.append_markdown_message("Error", str(e), is_error=True)
            self.llm_dropdown.setCurrentText("None")
    
    def execute_command(self):
        """Handle command execution"""
        if not self.cfd_software:
            self.append_markdown_message("Error", "No CFD software selected", is_error=True)
            return
            
        command = self.cmd_input.text()
        if not command:
            self.append_markdown_message("Error", "No command specified", is_error=True)
            return
            
        try:
            self.cfd_software.run_command(command, {})
            self.append_markdown_message("System", f"Executed command: `{command}`")
        except Exception as e:
            self.append_markdown_message("Error", str(e), is_error=True)
    
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
            
            self.append_markdown_message(None, "\n")
            self.append_markdown_message("You", message)
            self.append_markdown_message(None, "\n")
            QApplication.processEvents()
            
            try:
                # Get complete response
                response = self.llm_agent.return_response(message)
                
                # Start with Assistant: header
                self.append_markdown_message("Assistant", "")
                
                # Accumulate the complete response
                full_response = ""
                current_line = ""
                
                for event in response:
                    if hasattr(event.choices[0].delta, 'content'):
                        content = event.choices[0].delta.content
                        if content is not None:
                            full_response += content
                            current_line += content
                            
                            # If we have a newline, render the current line with markdown
                            if '\n' in current_line:
                                lines = current_line.split('\n')
                                # Keep the last part that doesn't end with newline for next iteration
                                current_line = lines[-1]
                                
                                # Process all complete lines
                                for line in lines[:-1]:
                                    if line:  # Only process non-empty lines
                                        try:
                                            html = markdown2.markdown(line, extras=['fenced-code-blocks', 'tables'])
                                            self.append_markdown_message(None, html)
                                        except:
                                            # If markdown fails, just show the plain line
                                            self.append_markdown_message(None, line)
                                    self.append_markdown_message(None, "\n")
                                    
                            QApplication.processEvents()
                
                # Process any remaining content
                if current_line:
                    try:
                        html = markdown2.markdown(current_line, extras=['fenced-code-blocks', 'tables'])
                        self.append_markdown_message(None, html)
                    except:
                        self.append_markdown_message(None, current_line)
                
            except Exception as e:
                self.append_markdown_message("Error", str(e), is_error=True)
            
            self.append_markdown_message(None, "\n")
            # Re-enable the send button
            self.send_btn.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = WhittleMainWindow()
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
