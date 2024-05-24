# import os

# def replace_words_in_files(directory, old_word, new_word):
#     # Klasördeki tüm dosyaları döngüye alır
#     for filename in os.listdir(directory):
#         if filename.endswith(".html"):  # Sadece.txt dosyalarını işler
#             file_path = os.path.join(directory, filename)
            
#             # Dosyayı okur
#             with open(file_path, 'r', encoding='utf-8') as file:
#                 lines = file.readlines()
                
#             # Her satırı döngüye alır ve belirli kelimenin yerini değiştirir
#             new_lines = []
#             for line in lines:
#                 new_line = line.replace(old_word, new_word)
#                 new_lines.append(new_line)
            
#             # Değiştirilmiş satırları yeni dosyaya yazar
#             with open(file_path, 'w', encoding='utf-8') as file:
#                 file.writelines(new_lines)

# # Kullanımı
# replace_words_in_files('/home/nur/Desktop/kasapbasi/hospitalmanagement-master/templates/school', 'symptom', 'reason')


# # # import os

# # # def rename_files_in_directory(directory, old_word, new_word):
# # #     # Klasördeki tüm dosyaları döngüye alır
# # #     for filename in os.listdir(directory):
# # #         # Dosya adı belirli kelimeye sahipse
# # #         if old_word in filename:
# # #             # Yeni dosya adını oluştur
# # #             new_filename = filename.replace(old_word, new_word)
            
# # #             # Dosyanın mevcut yolunu ve yeni yolunu belirle
# # #             old_file_path = os.path.join(directory, filename)
# # #             new_file_path = os.path.join(directory, new_filename)
            
# # #             # Dosyayı yeniden adlandır
# # #             os.rename(old_file_path, new_file_path)

# # # # Kullanımı
# # # rename_files_in_directory('//home/nur/Desktop/kasapbasi/hospitalmanagement-master/templates/school', 'hospital', 'school')


# venv sorunu için;
# pip install django==3.0.5
# pip install django-widget-tweaks
# pip install xhtml2pdf
# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver
# 1966  python manage.py createsuperuser

