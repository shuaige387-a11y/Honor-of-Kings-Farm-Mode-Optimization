# King of Glory: Farm Mode Optimizer

An automated scheduling tool that uses mathematical optimization to maximize weekly profits in the **King of Glory (Honor of Kings)** Farm Mode.

## 📖 Introduction

In the King of Glory Farm Mode, players manage **1-24 plots** of land (this number will change as you make progress). This project uses **Linear Programming (LP)** to generate an optimized 168-hour (7 days/a full week) planting schedule that accounts for your specific sleep routine and the weekend bonus window.

## ✨ Key Features

* **Sleep-Aware Logic:** Automatically avoids scheduling harvests during your sleep intervals. Sleep intervals are self-defined, which means users can modify these intervals according to their need.
* **Weekend Multiplier:** Intelligently shifts high-value crops to mature during the 2x revenue period (Saturday & Sunday).
* **Global Optimization:** Finds the absolute best combination of crops for the entire week.

## 🛠️ Installation

```bash
pip install pyomo
pip install appsi