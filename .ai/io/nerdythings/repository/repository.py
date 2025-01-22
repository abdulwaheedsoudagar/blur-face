from abc import ABC, abstractmethod

class Repository(ABC):
    
    @abstractmethod
    def post_comment_to_line(self, text, commit_id, file_path, line):
        pass
    
    @abstractmethod
    def post_comment_general(self, text):
        pass

class RepositoryError(Exception):
    pass