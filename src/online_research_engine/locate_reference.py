import re


class ReferenceLocator:
    def __init__(self, gpt_answer: str, serper_response: dict):
        self.gpt_answer = gpt_answer
        self.serper_response = serper_response

    def locate_source(self):
        """
        Returns a "list of information sources" for all "quoted sentences" in the GPT answer,
        such as web page title, URL, timestamp, original quoted text, etc.
        """
        # Split the answer into content and references parts
        splitted_answer = self.gpt_answer.split("\nReferences:")
        if len(splitted_answer) != 2:
            return -1

        answer_content = splitted_answer[0]  # Content part
        answer_references = splitted_answer[1]  # References part

        # Process the content to find sentences with references
        sentences_with_index = self._handle_sentences_in_answer(answer_content)
        # Match these sentences with their corresponding references
        sentences_with_references = self._match_references(
            answer_references, sentences_with_index
        )
        # Match web information with the found references
        reference_cards = self._match_web_info(sentences_with_references)

        return reference_cards

    def _handle_sentences_in_answer(self, answer_content: str):
        """
        Finds and processes all the sentences in the GPT's answer that contain references.
        """
        content_pattern = r"(?<=[\n\.\!]).*?\[\d+\]"
        matched_sentences = re.findall(content_pattern, answer_content)

        sentences_with_index = []
        for sentence in matched_sentences:
            sent, index = sentence.split(" [")
            index = int(index[:-1])
            sentences_with_index.append({"index": index, "sent": sent})

        return sentences_with_index

    def _match_references(self, answer_references: str, sentences_with_index: list):
        """
        Matches the original sentences with their corresponding reference URLs and quoted sentences.
        """
        # Extract reference indices, URLs, and quoted sentences
        index_pattern = r"\[\d+\]"
        index_list = re.findall(index_pattern, answer_references)

        url_pattern = r"https://[^\n]+"
        url_list = re.findall(url_pattern, answer_references)

        source_pattern = r"Quoted sentence: (.*?)\n"
        source_list = re.findall(source_pattern, answer_references)

        reference_with_index = [
            {
                "index": int(index_list[i][1:-1]),
                "url": url_list[i],
                "source": source_list[i],
            }
            for i in range(len(index_list))
        ]

        sentences_with_references = []
        for dict1 in sentences_with_index:
            for dict2 in reference_with_index:
                if dict1["index"] == dict2["index"]:
                    dict1.update({"url": dict2["url"], "source": dict2["source"]})
                    sentences_with_references.append(dict1)

        return sentences_with_references

    def _match_web_info(self, sentences_with_references: list):
        """
        Matches the sentences with references to the corresponding web information.
        """
        # Retrieve the web information (titles, timestamps, snippets) for each reference
        url_index_list = self.serper_response["links"]
        reference_cards = [
            {
                "titles": self.serper_response["titles"][
                    url_index_list.index(reference["url"])
                ],
                # 'time': self.serper_response['time'][url_index_list.index(reference['url'])],
                "snippets": self.serper_response["snippets"][
                    url_index_list.index(reference["url"])
                ],
                **reference,
            }
            for reference in sentences_with_references
        ]

        return reference_cards
