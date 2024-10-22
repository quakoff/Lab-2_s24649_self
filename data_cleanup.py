import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

# Konfiguracja loggera
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())


def main():
    try:
        # Wczytaj dane z CSV
        df = pd.read_csv('data_from_sheets.csv')
        logging.info("Dane zostały wczytane z pliku CSV.")

        # Informacje o danych
        total_rows = df.shape[0]
        total_columns = df.shape[1]
        logging.info(f"Liczba wierszy przed czyszczeniem: {total_rows}")
        logging.info(f"Liczba kolumn: {total_columns}")
        logging.info(f"Pierwsze 5 wierszy danych:\n{df.head()}")

        # Czyszczenie danych - liczenie braków
        missing_data_count = df.isnull().sum().sum()
        logging.info(f"Liczba brakujących danych: {missing_data_count}")

        # Ustalamy próg usuwania wierszy (np. 20%)
        missing_data_threshold = 0.3  # Można dostosować do swoich potrzeb
        df_cleaned = df.dropna(thresh=int((1 - missing_data_threshold) * df.shape[1]))
        removed_rows = total_rows - df_cleaned.shape[0]
        logging.info(f"Usunięto {removed_rows} wierszy z zbyt wieloma brakującymi danymi.")

        # Uzupełnianie braków - wybór metody uzupełnienia
        fill_method = 'średnia'  # Można ustawić na 'średnia', 'mediana', lub 'domyślna'

        # Liczba zmienionych wartości przed uzupełnieniem
        initial_missing_counts = df_cleaned.isnull().sum()

        if fill_method == 'średnia':
            df_filled = df_cleaned.fillna(df_cleaned.mean(numeric_only=True))
        elif fill_method == 'mediana':
            df_filled = df_cleaned.fillna(df_cleaned.median(numeric_only=True))
        elif fill_method == 'domyślna':
            default_value = 0  # Można dostosować do swoich potrzeb
            df_filled = df_cleaned.fillna(default_value)
        else:
            logging.error("Niepoprawna metoda uzupełniania.")
            raise ValueError("Niepoprawna metoda uzupełniania.")

        # Liczba zmienionych wartości po uzupełnieniu
        final_missing_counts = df_filled.isnull().sum()
        filled_values_per_column = initial_missing_counts - final_missing_counts
        total_filled_values = filled_values_per_column.sum()  # Liczba wszystkich uzupełnionych wartości

        logging.info(f"Uzupełniono {total_filled_values} brakujących wartości w kolumnach.")

        # Standaryzacja danych (średnia 0, odchylenie standardowe 1)
        scaler = StandardScaler()
        numeric_columns = df_filled.select_dtypes(include=[np.number]).columns.tolist()

        if numeric_columns:
            df_filled[numeric_columns] = scaler.fit_transform(df_filled[numeric_columns])
            logging.info("Dane zostały znormalizowane.")
        else:
            logging.warning("Brak kolumn numerycznych do standaryzacji.")

        # Zapisywanie wyczyszczonych danych do pliku
        df_filled.to_csv('cleaned_data.csv', index=False)
        logging.info("Wyczyszczone dane zapisano do pliku 'cleaned_data.csv'.")

        # Generowanie raportu
        report = f"""
           Liczba oryginalnych wierszy: {total_rows}
           Liczba usuniętych wierszy: {removed_rows} ({removed_rows / total_rows * 100:.2f}%)
           Liczba uzupełnionych wartości: {total_filled_values}
           Procent uzupełnionych danych: {total_filled_values / missing_data_count * 100:.2f}%
           Liczba pozostałych brakujących wartości: {df_filled.isnull().sum().sum()}
           Liczba zmienionych wartości: {total_filled_values}
           Procent usuniętych danych: {removed_rows / total_rows * 100:.2f}%
           
            
           """
        with open('report.txt', 'w') as report_file:
            report_file.write(report)

        logging.info("Raport wygenerowany i zapisany do pliku 'report.txt'.")

    except Exception as e:
        logging.error(f"Wystąpił błąd podczas przetwarzania danych: {e}")


if __name__ == "__main__":
    main()
