#!/usr/bin/python3
import time
import pygame
import random
import copy
pygame.init()
window_w=432
window_h=470
cell_w=48
cell_h=48
line_thk=3
WHITE=(255,255,255)
BLACK=(0,0,0)
BLUE=(0,100,200)
RED=(255,0,0)
GREEN=(0,255,0)
var = {}
f=pygame.font.SysFont("comicsans",40)
screen=pygame.display.set_mode((window_w,window_h))
screen.fill(WHITE,pygame.Rect(0,0,432,432))

def load_parameters(param):
  
  with open(param) as conf:
        for line in conf:
                if "=" in line:
                        name, value = line.split("=")
                        var[name] = str(value).rstrip()
                        var[name]=float(var[name])
  globals().update(var)

def load_sudoku(grid,sudoku_file):
  file=open(sudoku_file,'r')
  count=0
  while(1):
    i=count//int(var['sudoku_size'])
    j=count%int(var['sudoku_size'])
    char=file.read(1)
    if not char:
      break
    if char!=" " and char!="\n" and char!="\t":
      grid[i][j]=int(char)
      count=count+1
  file.close()

def display_sudoku(gridl,initial_fixed_cells):
  for i in range(int(var['sudoku_size'])):
    for j in range(int(var['sudoku_size'])):
      if gridl[i][j]!=0:
        b=pygame.draw.rect(screen,BLUE,pygame.Rect(j*cell_w,i*cell_h,cell_w,cell_h,),0)
        text=f.render(str(gridl[i][j]),1,BLACK)
        screen.blit(text,(j*cell_w+15,i*cell_h+int(var['sudoku_size'])))
        initial_fixed_cells.append(i*int(var['sudoku_size'])+j)
  for i in range(int(var['sudoku_size'])):
    if i%3==0:
      pygame.draw.line(screen,BLACK,(i*cell_w,0),(i*cell_w,window_h),line_thk)
      pygame.draw.line(screen,BLACK,(0,i*cell_h),(window_w,i*cell_h),line_thk)
    else:
      pygame.draw.line(screen,BLACK,(i*cell_w,0),(i*cell_w,window_h),1)
      pygame.draw.line(screen,BLACK,(0,i*cell_h),(window_w,i*cell_h),1)
  pygame.draw.rect(screen,WHITE,(316,442,106,20),0)
  f1=pygame.font.SysFont("comicsans",25)
  text=f1.render("Next update",1,BLACK)
  screen.blit(text,(320,442))
  pygame.display.update()
  while True:
    for ev in pygame.event.get():
      if ev.type == pygame.MOUSEBUTTONDOWN:
        mouse = pygame.mouse.get_pos()
        if 316<=mouse[0]<=422 and 442<= mouse[1]<=462:
          return 1

def constraint_propagation(gridt,value_sett):
  fcount=0
  change=True
  while(change):
    change=False
    for i in range(len(gridt)):
      for j in range(len(gridt[0])):
        if gridt[i][j]==0: 
          box_x=i-i%3
          box_y=j-j%3
          for k in range(len(gridt[0])):
            if gridt[i][k]!=0 and gridt[i][k] in value_sett[i*int(var['sudoku_size'])+j]:
              value_sett[i*int(var['sudoku_size'])+j].remove(gridt[i][k])
          for l in range(len(gridt)):
            if gridt[l][j]!=0 and gridt[l][j] in value_sett[i*int(var['sudoku_size'])+j]:
              value_sett[i*int(var['sudoku_size'])+j].remove(gridt[l][j])
          for m in range(3):
            for n in range(3): 
              if gridt[box_x+m][box_y+ n]!=0 and gridt[box_x+m][box_y+ n] in value_sett[i*int(var['sudoku_size'])+j]:
                value_sett[i*int(var['sudoku_size'])+j].remove(gridt[box_x+m][box_y+ n]) 
            
          if len(value_sett[i*int(var['sudoku_size'])+j])==1 and value_sett[i*int(var['sudoku_size'])+j][0]!=0:
            gridt[i][j]=value_sett[i*int(var['sudoku_size'])+j][0]
            change=True
            fcount=fcount+1
        else:
         value_sett[i*int(var['sudoku_size'])+j].clear()
         value_sett[i*int(var['sudoku_size'])+j].append(gridt[i][j])   
  return fcount
def pherome_construction(g_pheromone,value_set):
  for i in range(int(var['sudoku_size'])**2):
    for j in value_set[i]:
      g_pheromone[i][j-1]=1/(int(var['sudoku_size']))

def choose_value_err(cell,g_pheromone):
  q=random.uniform(0,1)
  cum_probability=[0]*int(var['sudoku_size'])
  if q<var['greediness']:
    cell_value=g_pheromone[cell].index(max(g_pheromone[cell])) +1
    return cell_value
  else:
    sum_list=sum(g_pheromone[cell])
    probability=[g_pheromone[cell][i]/sum_list for i in range(len(g_pheromone[cell]))]
    for i in range(len(g_pheromone[cell])):
      if i==0:
        cum_probability[i]=probability[i]
      else:
        cum_probability[i]=cum_probability[i-1]+probability[i]
    q1=random.uniform(0,1)
    for i in range(len(g_pheromone[cell])):
      if i==0 and (q1>0 and q1<=cum_probability[0]):
        cell_value=1
        return cell_value
      elif q1>cum_probability[i-1] and q1<=cum_probability[i]:
        cell_value=i+1
        return cell_value

def choose_value(cell,g_pheromone,vset):
  q=random.random()
  cum_probability=[0]*int(var['sudoku_size'])
  temp=[0]*int(var['sudoku_size'])
  for i in vset:
    temp[i-1]=g_pheromone[cell][i-1]
  if q<var['greediness']:
    cell_value=temp.index(max(temp)) +1
    return cell_value
  else:
    sum_list=sum(temp)
    probability=[temp[i]/sum_list for i in range(len(temp))]
    for i in range(len(g_pheromone[cell])):
      if i==0:
        cum_probability[i]=probability[i]
      else:
        cum_probability[i]=cum_probability[i-1]+probability[i]
    q1=random.random()
    for i in range(len(temp)):
      if i==0 and (q1>0 and q1<=cum_probability[0]):
        cell_value=1
        return cell_value
      elif q1>cum_probability[i-1] and q1<=cum_probability[i]:
        cell_value=i+1
        return cell_value

def local_pherom_update(cell_value,cell,g_pheromone):
  g_pheromone[cell][cell_value-1]=(1-var['local_pheroperator'])*g_pheromone[cell][cell_value-1] +(var['local_pheroperator'])*(1/(int(var['sudoku_size'])**2))
  
def global_pherom_update(gridl,g_pheromone,tau_best):
  for i in range(len(gridl)):
    for j in range(len(gridl[0])):
      celll=i*int(var['sudoku_size'])+j
      g_pheromone[celll][gridl[i][j]-1]=(1-var['global_pheroperator'])* g_pheromone[celll][gridl[i][j]-1] + tau_best

def update_sudoku(gridl,initial_fixed_cells):
  for i in range(int(var['sudoku_size'])):
      for j in range(int(var['sudoku_size'])):
        if gridl[i][j]!=0 and ((i*int(var['sudoku_size'])+j) not in initial_fixed_cells)  :
          b=pygame.draw.rect(screen,GREEN,pygame.Rect(j*cell_w,i*cell_h,cell_w,cell_h,),0)
          text=f.render(str(gridl[i][j]),1,BLACK)
          screen.blit(text,(j*cell_w+15,i*cell_h+int(var['sudoku_size'])))
        elif gridl[i][j]==0:
          b=pygame.draw.rect(screen,RED,pygame.Rect(j*cell_w,i*cell_h,cell_w,cell_h,),0)
  for i in range(int(var['sudoku_size'])):
    if i%3==0:
      pygame.draw.line(screen,BLACK,(i*cell_w,0),(i*cell_w,window_h),line_thk)
      pygame.draw.line(screen,BLACK,(0,i*cell_h),(window_w,i*cell_h),line_thk)
    else:
      pygame.draw.line(screen,BLACK,(i*cell_w,0),(i*cell_w,window_h),1)
      pygame.draw.line(screen,BLACK,(0,i*cell_h),(window_w,i*cell_h),1)
  pygame.draw.rect(screen,WHITE,(316,442,106,20),0)
  f1=pygame.font.SysFont("comicsans",25)
  text=f1.render("Next update",1,BLACK)
  screen.blit(text,(320,442))
  pygame.display.update()
  while True:
    for ev in pygame.event.get():
      if ev.type == pygame.MOUSEBUTTONDOWN:
        mouse = pygame.mouse.get_pos()
        if 316<=mouse[0]<=422 and 442<= mouse[1]<=462:
          return 1

class ant:
  grid=0
  value_set=0
  cell=0
  fixed_cell=0

def main():
  param=input("Enter parameters file: ") 
  sudoku_file=input("Enter sudoku file: ") 
  evolutions=int(input("Enter no of evolutions you want to see: ")) 
  
  load_parameters(param) #Load the parameters
  
  #define variables for the algorithm
  grid=[[0]*int(var['sudoku_size']) for i in range(int(var['sudoku_size']))]
  value_set=[[j for j in range(1,10)] for i in range(int(var['sudoku_size'])*int(var['sudoku_size']))]
  g_pheromone=[[0 for j in range(1,10)] for i in range(int(var['sudoku_size'])*int(var['sudoku_size']))]
  grid_c=[]
  initial_fixed_cells=[]
  load_sudoku(grid,sudoku_file) 

  #load the sudoku puzzle
  display_sudoku(grid,initial_fixed_cells)
  
  #Create ants and perform constraint propagation
  ants=[ant() for i in range(int(var['no_of_ants']))]  
  gbant=ant()
  fcellc=len(initial_fixed_cells)+constraint_propagation(grid,value_set)
  pherome_construction(g_pheromone,value_set)
  gbant.fixed_cell=0
  tau_best=0
  print(value_set)
  print("Started Solving")
  while(gbant.fixed_cell!=int(var['sudoku_size'])**2-fcellc): #This loop runs until the puzzle is solveds
    for i in range(int(var['no_of_ants'])):                            #This loop initialises ants with puzzle and initial_postition
      ants[i].grid=copy.deepcopy(grid)
      ants[i].value_set=copy.deepcopy(value_set)
      ants[i].cell=random.randint(0,80)
      ants[i].fixed_cell=0
    
    cell_left=int(var['sudoku_size'])**2
    while(cell_left):                                                  #This loop iterates through every cell
      for k in range(int(var['no_of_ants'])):                          #For eevry cell this loop iterates through every ant
        if ants[k].cell==81:
          ants[k].cell=0
        i=ants[k].cell//int(var['sudoku_size'])
        j=ants[k].cell%int(var['sudoku_size'])
        if len(ants[k].value_set[ants[k].cell])> 1:
          cell_value=choose_value(ants[k].cell,g_pheromone,ants[k].value_set[ants[k].cell])            #Choose a value(between 1 to 9) for a cell based on greediness and roulette wheel selection
          ants[k].grid[i][j]=cell_value
          ants[k].fixed_cell=ants[k].fixed_cell+constraint_propagation(ants[k].grid, ants[k].value_set) #Propagate the constraints with the chosen value
          ants[k].fixed_cell=ants[k].fixed_cell+1
          local_pherom_update(cell_value,ants[k].cell,g_pheromone)     #Update pheromone to make less likely for other ants to choose this value for this cell 
        ants[k].cell=ants[k].cell+ 1
      cell_left= cell_left-1      
    for j in range(int(var['no_of_ants'])):                            #This loop finds the best ant
      tau=var['global_pheroperator']*(int(var['sudoku_size'])/(int(var['sudoku_size'])**2 - ants[j].fixed_cell))
      if tau> tau_best:
        gbant.fixed_cell=ants[j].fixed_cell  
        gbant.grid=copy.deepcopy(ants[j].grid)
        gbant.value_set=copy.deepcopy(ants[j].value_set)
        tau_best=var['global_pheroperator']*(int(var['sudoku_size'])/(int(var['sudoku_size'])**2 - gbant.fixed_cell))
    global_pherom_update(gbant.grid,g_pheromone,tau_best)                            #update Pheromone values according to the best ant 
    tau_best=(1-var['best_evaporation'])*tau_best                                    #perform best value_evaporation
    grid_c.append(gbant.grid)
  print("finished")
  if len(grid_c)<evolutions:
    for i in range(len(grid_c)):
      update_sudoku(grid_c[i],initial_fixed_cells)
      print(i+1)
  if len(grid_c)>=evolutions:
    count=0
    div=len(grid_c)//evolutions
    for i in range(len(grid_c)):
      if ((i+1)%div)==0:
        update_sudoku(grid_c[i],initial_fixed_cells)
        print(i+1)
        count=count+1   
        if count==evolutions-1:
          break
    print(len(grid_c))
    update_sudoku(grid_c[-1],initial_fixed_cells) 
    
if __name__ =="__main__":
  main()
        
          
      
   

