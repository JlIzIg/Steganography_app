import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk
import random
import numpy as np
from skimage import io, color


def decode_message(st_image_path, T41, T42):

    sizeBlock = 16

    # Load and convert the image to YCbCr
    ImageStego = io.imread(st_image_path)
    ImageStego_ycbcr = color.rgb2ycbcr(ImageStego)
    imageStego = ImageStego_ycbcr[:, :, 0].astype(float)

    rows, cols = imageStego.shape
    d = 0
    message_rec = []

    # Traverse each 16x16 block in the image
    for i1 in range(0, rows, sizeBlock):
        for i2 in range(0, cols, sizeBlock):
            # Divide the 16x16 block into 4x4 sub-blocks
            block = imageStego[i1:i1 + sizeBlock, i2:i2 + sizeBlock]

            sub_blocks = [
                block[0:4, 0:4], block[0:4, 4:8], block[4:8, 0:4], block[4:8, 4:8],
                block[0:4, 8:12], block[0:4, 12:16], block[4:8, 8:12], block[4:8, 12:16],
                block[8:12, 0:4], block[8:12, 4:8], block[12:16, 0:4], block[12:16, 4:8],
                block[8:12, 8:12], block[8:12, 12:16], block[12:16, 8:12], block[12:16, 12:16]
            ]

            StructureT8 = np.array([1, 1, -1, -1])

            def calculate_code(sub_blocks, T):
                u_vals = [np.sum(sb * T) for sb in sub_blocks]
                y_vals = np.array(u_vals) - np.mean(u_vals)
                return np.sign(np.sum(y_vals * StructureT8))

            # Compute Code8 values for both T41 and T42 matrices
            Code8_1 = calculate_code(sub_blocks[:4], T41) + calculate_code(sub_blocks[:4], T42)
            Code8_2 = calculate_code(sub_blocks[4:8], T41) + calculate_code(sub_blocks[4:8], T42)
            Code8_3 = calculate_code(sub_blocks[8:12], T41) + calculate_code(sub_blocks[8:12], T42)
            Code8_4 = calculate_code(sub_blocks[12:], T41) + calculate_code(sub_blocks[12:], T42)

            StructurePOSITIVE = np.array([1, 1, -1, -1])
            StructureNEGATIVE = np.array([-1, -1, 1, 1])
            Code8 = np.array([Code8_1, Code8_2, Code8_3, Code8_4])

            # Summing only non-zero values
            sumValue = 0
            if Code8_1 != 0:
                sumValue += Code8_1
            if Code8_2 != 0:
                sumValue += Code8_2
            if Code8_3 != 0:
                sumValue -= Code8_3
            if Code8_4 != 0:
                sumValue -= Code8_4

            if sumValue == 0:
                numMatchingPOSITIVE = np.sum(Code8 == StructurePOSITIVE)
                numMatchingNEGATIVE = np.sum(Code8 == StructureNEGATIVE)
                if numMatchingPOSITIVE > numMatchingNEGATIVE:
                    bit = 1
                else:
                    bit = 0
            else:
                bit = np.sign(sumValue)
                if bit == -1:
                    bit = 0
            message_rec.append(bit)
            d += 1

    message_str = ''.join(['1' if bit == 1 else '0' for bit in message_rec])
    return message_str






def embed_message_in_image(image_path, T41, T42, message, output_path, QF):

    T8 = np.block([[T41 + T42, T41 + T42], [-(T41 + T42), -(T41 + T42)]])
    T16 = np.block([[T8, T8], [-T8, -T8]])

    sizeBlock = 16

    # Load and prepare the image
    Image = io.imread(image_path)
    rows, cols, channels = Image.shape

    # Crop image dimensions to be divisible by sizeBlock
    new_rows = (rows // sizeBlock) * sizeBlock
    new_cols = (cols // sizeBlock) * sizeBlock
    Image_cropped = Image[:new_rows, :new_cols, :]
    Image_cropped1 = color.rgb2ycbcr(Image_cropped)
    M = Image_cropped1[:, :, 0].astype(float)


    k=0
    for i1 in range(0, new_rows, sizeBlock):
        for i2 in range(0, new_cols, sizeBlock):
                # Embed random bits (-1 or 1) into each 16x16 block
                if k<len(message):
                    if message[k]=='0':
                            M[i1:i1 + sizeBlock, i2:i2 + sizeBlock] += (-1) * T16
                    else:
                            M[i1:i1 + sizeBlock, i2:i2 + sizeBlock] += T16
                    k+=1
                else:
                    M[i1:i1 + sizeBlock, i2:i2 + sizeBlock] =M[i1:i1 + sizeBlock, i2:i2 + sizeBlock]
    print(message)
    # Reconstruct the image
    Image_cropped1[:, :, 0] = M
    Image_cropped_rgb = color.ycbcr2rgb(Image_cropped1) * 255
    io.imsave(output_path, Image_cropped_rgb.astype(np.uint8), quality=QF)


class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diploma work (Zihinova Y.)")
        self.root.geometry("320x305")
        self.settings_image = ImageTk.PhotoImage(Image.open("icons/settings_icon.png").resize((25, 25)))
        self.app_icon = ImageTk.PhotoImage(
            Image.open("icons/icon_app.png").resize((25, 25)))
        self.root.iconphoto(False, self.app_icon)
        self.main_window()

        self.initialize_T4()

        # Variables to store mode, selected code words, and QF
        self.mode = tk.StringVar(value="Random Message")
        self.code_word_1 = tk.StringVar(value="Code4")
        self.code_word_2 = tk.StringVar(value="Code4")
        self.qf_value = tk.StringVar(value="70")  # Default QF value

    def initialize_T4(self):
        self.T4 = np.array([
            [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]],
            [[1, -1, 1, -1], [1, -1, 1, -1], [1, -1, 1, -1], [1, -1, 1, -1]],
            [[1, 1, -1, -1], [1, 1, -1, -1], [1, 1, -1, -1], [1, 1, -1, -1]],
            [[1, -1, -1, 1], [1, -1, -1, 1], [1, -1, -1, 1], [1, -1, -1, 1]],
            [[1, 1, 1, 1], [-1, -1, -1, -1], [1, 1, 1, 1], [-1, -1, -1, -1]],
            [[1, -1, 1, -1], [-1, 1, -1, 1], [1, -1, 1, -1], [-1, 1, -1, 1]],
            [[1, 1, -1, -1], [-1, -1, 1, 1], [1, 1, -1, -1], [-1, -1, 1, 1]],
            [[1, -1, -1, 1], [-1, 1, 1, -1], [1, -1, -1, 1], [-1, 1, 1, -1]],
            [[1, 1, 1, 1], [1, 1, 1, 1], [-1, -1, -1, -1], [-1, -1, -1, -1]],
            [[1, -1, 1, -1], [1, -1, 1, -1], [-1, 1, -1, 1], [-1, 1, -1, 1]],
            [[1, 1, -1, -1], [1, 1, -1, -1], [-1, -1, 1, 1], [-1, -1, 1, 1]],
            [[1, -1, -1, 1], [1, -1, -1, 1], [-1, 1, 1, -1], [-1, 1, 1, -1]],
            [[1, 1, 1, 1], [-1, -1, -1, -1], [-1, -1, -1, -1], [1, 1, 1, 1]],
            [[1, -1, 1, -1], [-1, 1, -1, 1], [-1, 1, -1, 1], [1, -1, 1, -1]],
            [[1, 1, -1, -1], [-1, -1, 1, 1], [-1, -1, 1, 1], [1, 1, -1, -1]],
            [[1, -1, -1, 1], [-1, 1, 1, -1], [-1, 1, 1, -1], [1, -1, -1, 1]]
        ])

    def get_T_value(self, code_word):
        # Map code words to their corresponding T4 matrices
        code_word_to_index = {
            "Code1": 0,
            "Code2": 1,
            "Code3": 2,
            "Code4": 3,
            "Code5": 4,
            "Code6": 5,
            "Code7": 6,
            "Code8": 7,
            "Code9": 8,
            "Code10": 9,
            "Code11": 10,
            "Code12": 11,
            "Code13": 12,
            "Code14": 13,
            "Code15": 14,
            "Code16": 15
        }
        index = code_word_to_index.get(code_word, 0)  # Default to first matrix if not found
        return self.T4[index]  # Return the corresponding T4 matrix

    def main_window(self):
        # Main Window
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Button(self.root, image=self.settings_image, command=self.settings_window).pack(pady=10)
        tk.Button(self.root, text="Embed AI", command=self.embed_ai_window).pack(pady=20)
        tk.Button(self.root, text="Extract AI", command=self.extract_ai_window).pack(pady=10)

    def settings_window(self):
        # Settings Window
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Mode").pack(pady=5)
        tk.Radiobutton(self.root, text="Conscious Message", variable=self.mode, value="Conscious Message").pack()
        tk.Radiobutton(self.root, text="Random Message", variable=self.mode, value="Random Message").pack()

        tk.Label(self.root, text="Code Words").pack(pady=5)
        code_words = ["Code1", "Code2", "Code3","Code4", "Code5", "Code6", "Code7", "Code8", "Code9", "Code10", "Code11", "Code12", "Code13", "Code14", "Code15", "Code16" ]  # Sample code words
        tk.OptionMenu(self.root, self.code_word_1, *code_words).pack()
        tk.OptionMenu(self.root, self.code_word_2, *code_words).pack()

        # Adding QF selection dropdown
        tk.Label(self.root, text="QF").pack(pady=5)
        qf_options = [str(i) for i in range(10, 101, 10)]  # QF values from 10 to 100 in steps of 10
        tk.OptionMenu(self.root, self.qf_value, *qf_options).pack()

        tk.Button(self.root, text="Apply", command=self.apply_settings).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.main_window).pack(pady=5)

    def apply_settings(self):
        # Save selected settings
        self.applied_mode = self.mode.get()
        self.applied_code_word_1 = self.code_word_1.get()
        self.applied_code_word_2 = self.code_word_2.get()
        self.applied_qf = self.qf_value.get()
        messagebox.showinfo("Settings", f"Mode: {self.applied_mode}\nCode Words: {self.applied_code_word_1}, {self.applied_code_word_2}\nQF: {self.applied_qf}")

    def embed_ai_window(self):
        self.home_image = ImageTk.PhotoImage(Image.open("icons/icon_home.png").resize((25, 25)))

        # Embed AI Window
        for widget in self.root.winfo_children():
            widget.destroy()

        def embed_message():
            image_path = file_label.cget("text").replace("File: ", "")
            message = input_zone.get("1.0", tk.END).strip()
            print("Embedded:")
            print(message)
            if any(c not in "01" for c in message):
                message=message+"/end"
                # Convert each character to its 8-bit binary representation
                message = ''.join(format(ord(c), '08b') for c in message)
            # Get T41 and T42 based on selected code words
            T41 = self.get_T_value(self.applied_code_word_1)
            T42 = self.get_T_value(self.applied_code_word_2)

            # Construct output path
            output_path = image_path.rsplit('.', 1)[0] + "_enc.jpg"  # Save as JPEG

            # Get QF value from settings
            QF = int(self.applied_qf)

            # Call the embed_message_in_image function
            embed_message_in_image(image_path, T41, T42, message, output_path, QF)
            messagebox.showinfo("Success", f"Message embedded successfully in {output_path}")

        def choose_file():
            file_path = filedialog.askopenfilename()
            if file_path:
                file_label.config(text=f"File: {file_path}")
                if self.applied_mode == "Conscious Message":
                    ok_button.config(state="normal")

        tk.Button(self.root, text="Choose File", command=choose_file).pack(pady=5)
        file_label = tk.Label(self.root, text="No file chosen")
        file_label.pack()

        input_zone = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=30, height=5)
        input_zone.pack(pady=5)
        if self.applied_mode == "Random Message":
            random_message = ''.join(random.choice(['0', '1']) for _ in range(100))
            input_zone.insert(tk.END, random_message)


        ok_button = tk.Button(self.root, text="OK", state="disabled" if self.applied_mode == "Conscious Message" else "normal")
        ok_button.pack(pady=5)
        ok_button.config(command=embed_message)

        tk.Button(self.root, image=self.home_image, command=self.main_window).pack(pady=5)



    def extract_ai_window(self):
        self.home_image = ImageTk.PhotoImage(Image.open("icons/icon_home.png").resize((25, 25)))

        # Extract AI Window
        for widget in self.root.winfo_children():
            widget.destroy()

        def choose_file():
            file_path = filedialog.askopenfilename()
            if file_path:
                file_label.config(text=f"File: {file_path}")
                extract_button.config(state="normal")

        tk.Button(self.root, text="Choose File", command=choose_file).pack(pady=5)
        file_label = tk.Label(self.root, text="No file chosen")
        file_label.pack()

        def rec_message():
            image_path = file_label.cget("text").replace("File: ", "")

            # Get T41 and T42 based on selected code words
            T41 = self.get_T_value(self.applied_code_word_1)
            T42 = self.get_T_value(self.applied_code_word_2)

            # Decode the message as a binary string
            binary_message = decode_message(image_path, T41, T42)

            # If mode is not "Random Message," convert the binary message to characters
            if self.applied_mode != "Random Message":
                # Group bits into bytes and convert each to a character
                characters = [chr(int(binary_message[i:i + 8], 2)) for i in range(0, len(binary_message), 8)]
                message = ''.join(characters)
                message = message.split("/end")[0]
            else:
                message = binary_message[0:100] # Keep the message in binary form if it's random

            # Display the decoded message
            print("Decoded:")
            print(message)

            output_zone.config(state="normal")
            output_zone.delete(1.0, tk.END)
            output_zone.insert(tk.END, message)  # Insert the decoded message
            output_zone.config(state="disabled")

            # Display success message in a popup
            messagebox.showinfo("Success", "Message decrypted successfully")

        extract_button = tk.Button(self.root, text="Extract", state="disabled")
        extract_button.pack(pady=5)
        extract_button.config(command=rec_message)
        output_zone = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=30, height=5, state="disabled")
        output_zone.pack(pady=5)

        tk.Button(self.root, image=self.home_image, command=self.main_window).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()
