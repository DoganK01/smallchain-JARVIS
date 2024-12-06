from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

import re
from typing import List, Callable

class CRecursiveTextSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int, length_function: Optional[Callable[[str], int]] = len, is_separator_regex: bool = False, keep_separator: bool = False):
        """
        Initialize the text splitter.
        
        :param chunk_size: Maximum size of each chunk.
        :param is_separator_regex: Whether to treat separators as regex.
        :param keep_separator: Whether to keep the separator in the output chunks.
        """
        self._seperators = ["\n\n", "\n", " ", ""]
        self._chunk_size = chunk_size
        self._length_function = length_function
        self._is_separator_regex = is_separator_regex
        self._keep_separator = keep_separator
    
    def _split_text_with_regex(self, text: str, separator: str, keep_separator: bool) -> List[str]:
        """
        Splits text using a regex separator and optionally retains the separator.
        """
        if keep_separator:
            return re.split(f"({separator})", text)
        else:
            return re.split(separator, text)
    
    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """
        Merges splits into chunks, ensuring they meet the chunk size constraint.
        """
        chunks = []
        current_chunk = ""
        for part in splits:
            if len(current_chunk) + len(part) + len(separator) > self._chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = part
            else:
                current_chunk += (separator + part) if current_chunk else part
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    def _split_text(self, text: str, separators: Optional[List[str]]) -> List[str]:
        """
        Split incoming text recursively and return chunks.
        """
        final_chunks = []
        # determine the appropriate separator
        separator = separators[-1]
        new_separators = []
        for i, sep in enumerate(separators):
            escaped_sep = sep if self._is_separator_regex else re.escape(sep)
            if not sep:
                separator = sep
                break
            if re.search(escaped_sep, text):
                separator = sep
                new_separators = separators[i + 1:]
                break
        
        # perform splitting using the determined separator
        escaped_sep = separator if self._is_separator_regex else re.escape(separator)
        splits = self._split_text_with_regex(text, escaped_sep, self._keep_separator)

        # process splits, handling recursive splitting for long chunks
        _good_splits = []
        final_separator = "" if self._keep_separator else separator
        for split in splits:
            if self._length_function(split) < self._chunk_size:
                _good_splits.append(split)
            else:
                if _good_splits:
                    merged = self._merge_splits(_good_splits, final_separator)
                    final_chunks.extend(merged)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(split)
                else:
                    final_chunks.extend(self._split_text(split, new_separators))
        if _good_splits:
            final_chunks.extend(self._merge_splits(_good_splits, final_separator))
        return final_chunks
    
    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self._seperators)


# Example usage
if __name__ == "__main__":
    text = """The standard Lorem Ipsum passage, used since the 1500s
"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

Section 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC
"Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"

1914 translation by H. Rackham
"But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?"

Section 1.10.33 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC
"At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat."

1914 translation by H. Rackham
"On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue; and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided. But in certain circumstances and owing to the claims of duty or the obligations of business it will frequently occur that pleasures have to be repudiated and annoyances accepted. The wise man therefore always holds in these matters to this principle of selection: he rejects pleasures to secure other greater pleasures, or else he endures pains to avoid worse pains."""
    separators = ["\n\n", "\n", " ", ""]
    #separators=["\n\n"]

    csplitter = CRecursiveTextSplitter(chunk_size=200, chunk_overlap=0)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
    chunks = csplitter.split_text(text)
    chunks_langchain = text_splitter.split_text(text)
    if chunks is not None:
        for i, chunk in enumerate(chunks):
            print(f"Chunk {i + 1}: {chunk}")

    for i, chunk in enumerate(chunks_langchain):
        print(f"Chunk LANGCHAİN {i + 1}: {chunk}")

    

    
