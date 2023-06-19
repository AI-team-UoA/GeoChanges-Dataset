from happytransformer import HappyTextToText, TTSettings
import torch

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

args = TTSettings(num_beams=5, min_length=1, max_length=100, early_stopping=True)

def grammar_correction(question):
    # corrected_question_list=[]
    # print(question_list)
    # for text in question_list:
    corrected_text= happy_tt.generate_text("grammar: "+question, args=args).text
    if question!=corrected_text:
        return corrected_text
    else:
        return ""
    