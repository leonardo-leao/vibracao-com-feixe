import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.fft as scipy
from datetime import datetime, timedelta

def replace(str, wordsToReplace, replace):
    for i in range(len(wordsToReplace)):
        str = str.replace(wordsToReplace[i], replace)
    return str

def leituraEstacaoSismografica(filename):
    file = open(filename).read()
    file = file.split("\n")
    time = []
    estacao_sism = {"Data": []}
    for i in range(len(file)):
        if "$" in file[i]:
            line_content = replace(file[i], ["$", " "], "")
            key, value = line_content.split("=")
            if key == "Time":
                initialTime = datetime.strptime(value[0:-3], "%Y:%j:%H:%M:%S.%f")
                estacao_sism[key] = initialTime
                initialTime = initialTime - timedelta(microseconds=1e4)
            else:
                estacao_sism[key] = float(value) if value.isnumeric() else value
        else:
            if file[i] != "":
                estacao_sism["Data"].append(float(file[i]))
                initialTime = initialTime + timedelta(microseconds=1e4)
                time.append(initialTime)
    return (time, [estacao_sism["Data"]])

def leituraSismometro(filename, initialDate = None, sampleRate = 1000):
    file = open(filename).read()
    file = file.split("\n")
    horarios = []
    valores = [[] for _ in range(len(file[0].split("\t"))-1)]
    for i in range(len(file)-1):
        line = file[i].split("\t")
        x = line[0]; y = line[1:]
        if initialDate != None:
            horarios.append(initialDate)
            initialDate += timedelta(seconds = 1/sampleRate)
        else:
            horarios.append(float(x.replace(",", ".")))
        for j in range(len(y)):
            valores[j].append(float(y[j].replace(",", ".").replace("\x00", "")))
    return (horarios, valores)

def identificaArquivos(diretorio):
    arquivos = []
    for sub in os.listdir(diretorio):
        if ".txt" in sub or ".atr" in sub:
            if "Ignorar" not in diretorio:
                arquivos.append(f"{diretorio}/{sub}")
        else:
            for arquivo in identificaArquivos(f"{diretorio}/{sub}"):
                arquivos.append(arquivo)
    return arquivos

def fft(signal, sampleRate):
    n_samples = len(signal)
    T = 1/sampleRate
    yf = scipy.fft(signal)
    xf = scipy.fftfreq(n_samples, T)[:n_samples//2]
    return (xf, np.abs(yf[0:n_samples//2]))

def plot(x, y, titulo, ylim = None, ylabel = None, addFFT=False):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    if addFFT == False:
        fig, ax = plt.subplots(len(x), figsize=(14, 3*len(x)))
        if len(x) == 1:
            ax = [ax]
        for i in range(len(x)):
            ax[i].plot(x[i], y[i], color=colors[i])
            ax[i].set_ylabel(ylabel)
            if type(x[i][0]) != float:
                ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M, %b-%d'))
            ax[i].ticklabel_format(axis="y", style="sci", scilimits=(0,0))
    else:
        fig, ax = plt.subplots(len(x)//2, 4, figsize=(18, 2*len(x)//2))
        row, column = (0, 0)
        for i in range(len(x)):
            if column == 4:
                row += 1
                column = 0

            ax[row][column].plot(x[i], y[i], color=colors[i])
            ax[row][column].set_ylabel(ylabel)
            ax[row][column].ticklabel_format(axis="y", style="sci", scilimits=(0,0))
            if type(x[i][0]) != float:
                ax[i][0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M, %b-%d'))

            if column == 0:
                ax[row][column].set_title("Bloco")
            elif column == 2:
                ax[row][column].set_title("Piso")
            
            column += 1

            xf, yf = fft(y[i], 1000)
            ax[row][column].plot(xf[150:], yf[150:], color=colors[i])
            ax[row][column].set_ylabel("Amplitude")
            ax[row][column].set_xlabel("Frequency [Hz]")
            ax[row][column].set_xlim([0,100])
            ax[row][column].ticklabel_format(axis="y", style="sci", scilimits=(0,0))
            
            column += 1

    plt.suptitle(titulo)
    plt.ylim(ylim)
    plt.tight_layout()
    plt.show()

# Diretório de dados
dir = r"C:\Users\leonardo.leao\Desktop\Medidas de Vibração\Análise de vibração do feixe (16-05-2022)\Medidas-vibracao-16-05-22\Acel_Piso"
saida = "C:/Users/leonardo.leao/Desktop/Medidas de Vibração/Análise de compactação do solo (17-05-2022)/Compactacao 17-05-2022/imagens"

# Obtém os arquivos de dados
for diretorio in os.listdir(dir):
    arquivos = identificaArquivos(f"{dir}/{diretorio}")
    horario = []; valores = []
    for i in range(len(arquivos)):
        if "PSD" not in arquivos[i]:
            if diretorio == "Estação Sismográfica":
                x, y = leituraEstacaoSismografica(arquivos[i])
            else:
                x, y = leituraSismometro(arquivos[i])
            for j in range(len(y)):
                horario.append(x)
                valores.append(y[j])
    if len(horario) > 0:
        if "compactação" in diretorio:
            plot(horario, valores, diretorio, [-0.0003, 0.0003], ylabel="Gravidade (g)")
        else:
            #for i in range(len(valores)):
            #    print(len(horario[i]), len(valores[i]))
            plot(horario, valores, diretorio, ylabel="Gravidade (g)", addFFT=True)
