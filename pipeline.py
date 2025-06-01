# pipeline.py
import os
from system_monitor import system_monitor
from llm import run_llm
from document_processor import DocumentProcessor
from config import TOP_K_CHUNKS
from logger import logger

# Initialize document processor
doc_processor = DocumentProcessor()

@system_monitor.monitor
def run_pipeline(prompt, file_path=None):
    """Run the pipeline with optional document context."""
    try:
        # If we have a document, get relevant chunks
        if file_path:
            # Process document if not already done
            if not doc_processor.chunks:
                doc_processor.process_document(file_path)
            
            # Get the user's question (last line of the prompt)
            user_question = prompt.split('\n')[-2].replace('Human: ', '') if '\n' in prompt else prompt
            logger.info(f"Processing question: {user_question}")
            
            # Find relevant chunks
            relevant_chunks = doc_processor.search(user_question, top_k=TOP_K_CHUNKS)
            
            if relevant_chunks:
                # Combine relevant chunks with their context
                doc_context = "\n\n".join(chunk for chunk, score in relevant_chunks)
                
                # Add document context to the prompt
                full_prompt = f"""Context from document:
{doc_context}

Current conversation:
{prompt}"""
                logger.info("Added document context to prompt")
            else:
                logger.info("No relevant document sections found, using prompt without context")
                full_prompt = prompt
        else:
            logger.info("No document provided, using prompt without context")
            full_prompt = prompt
        
        # Get response from LLM
        logger.info("Sending prompt to LLM...")
        response = run_llm(full_prompt)
        logger.info("Received response from LLM")
        return response
        
    except Exception as e:
        logger.error(f"Error in pipeline: {str(e)}")
        return f"Error in pipeline: {str(e)}"

