import pandas as pd
from openai import OpenAI
import random
import os

class DataAugmentor:
    def __init__(self, client):
        self.client = client

    def generate_synonym_sentence(self, prompt, num_variations=5):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que gera variações de frases usando sinônimos."},
                {"role": "user", "content": f"Gere {num_variations} variações da frase: '{prompt}'."}
            ],
            max_tokens=500,
            n=1,
            temperature=0.7
        )
        variações = response.choices[0].message.content.strip().split("\n")
        return [variação.strip() for variação in variações if variação]

    def save_to_csv_append(self, output_file, df):
        file_exists = os.path.isfile(output_file)
        df.to_csv(output_file, mode='a', header=not file_exists, index=False, encoding='utf-8')

    def augment_intentions(self, df, target_samples=220):
        intention_counts = df['Intencao'].value_counts().to_dict()

        all_new_samples = pd.DataFrame()

        for intencao, count in intention_counts.items():
            missing_samples = target_samples - count
            if missing_samples > 0:
                print(f"Intenção '{intencao}' precisa de {missing_samples} novas amostras para atingir {target_samples}.")

                perguntas_intencao = df[df['Intencao'] == intencao]
                new_samples = []
                while missing_samples > 0:
                    for _, row in perguntas_intencao.iterrows():
                        if missing_samples <= 0:
                            break
                        pergunta = row['Pergunta Original']
                        resposta_real = row['Resposta']

                        num_variations = min(5, missing_samples)
                        variações = self.generate_synonym_sentence(pergunta, num_variations)

                        for variação in variações:
                            new_sample = {
                                "Intencao": intencao,
                                "Pergunta Original": pergunta,
                                "Variação": variação,
                                "Resposta": resposta_real  
                            }
                            new_samples.append(new_sample)
                            missing_samples -= 1
                            if missing_samples <= 0:
                                break

                all_new_samples = pd.concat([all_new_samples, pd.DataFrame(new_samples)])

        return all_new_samples

    def save_augmented_data(self, output_file, new_samples):
        file_exists = os.path.isfile(output_file)
        new_samples.to_csv(output_file, mode='a', header=not file_exists, index=False)
        print(f"Amostras adicionadas com sucesso. Total de novas amostras: {len(new_samples)}")


def load_data(file_path):
    return pd.read_csv(file_path)

def random_test_phrases():
    return [
        "Como faço uma transferência?",
        "Qual o meu saldo disponível?",
        "Como posso atualizar meu endereço?",
        "Quais são as taxas de transferência?",
        "Meu pagamento foi processado?",
    ]



def local_test(augmentor):
    
    test_data = {
        'Intencao': ['Transferência', 'Saldo', 'Endereço', 'Taxas', 'Pagamento'],
        'Pergunta Original': random_test_phrases(),
        'Resposta': [augmentor.generate_synonym_sentence(phrase)[0] for phrase in random_test_phrases()]
    }
    df_test = pd.DataFrame(test_data)

    
    test_output_file = 'test_perguntas_e_respostas_geradas.csv'

    
    new_samples = augmentor.augment_intentions(df_test, target_samples=10)

    
    augmentor.save_augmented_data(test_output_file, new_samples)

    
    df_final_test = pd.read_csv(test_output_file)
    print(df_final_test)


if __name__ == "__main__":
    client = OpenAI(api_key='')
    augmentor = DataAugmentor(client)

    
    local_test(augmentor)
