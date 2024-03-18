#!/usr/bin/env python
# coding: utf-8


from collections import namedtuple

from loren_frank_data_processing.core import logger


try:
  import pipeline.spike_data_to_dataframe_up_to_date_version as sdd
  import pipeline.subdivision_by_behav_state_up_to_date_version as behav
  import pipeline.task_up_to_date_version as task
  import pipeline.df_subdivision_by_theme as divis
  import pipeline.sum_and_seperate_spike_trains as sum_sep

except:
  import spike_data_to_dataframe_up_to_date_version as sdd
  import subdivision_by_behav_state_up_to_date_version as behav
  import task_up_to_date_version as task
  import df_subdivision_by_theme as divis
  import sum_and_seperate_spike_trains as sum_sep



Animal = namedtuple('Animal', {'short_name', 'directory'})

'''
conley = Animal('/home/bellijjy/Conley.tar/Conley', 'con')
dave = Animal('/home/bellijjy/Dave.tar/Dave/Dave', 'dav')
chapati = Animal('/home/bellijjy/Chapati.tar/Chapati/Chapati', 'cha')
corriander = Animal('/home/bellijjy/Corriander.tar/Corriander', 'Cor')
dudley = Animal('/home/bellijjy/Dudley', 'dud')
bond = Animal('/home/bellijjy/Bond', 'bon')
'''
frank = Animal('/local2/Jan/Frank/Frank', 'fra')
government = Animal('/local2/Jan/Government/Government', 'gov') # for some reason, instead of 'gov', there was 'fra' here
egypt = Animal('/local2/Jan/Egypt/Egypt', 'egy')
remy = Animal('/local2/Jan/Remy/Remy', 'remy')
five = Animal("/home/dekorvyb/Downloads/Fiv", "Fiv")
bon = Animal("/home/dekorvyb/Downloads/Bon", "bon")


animals = {#'con': Animal('con','/home/bellijjy/Conley.tar/Conley'),
           #'Cor': Animal('Cor','/home/bellijjy/Corriander.tar/Corriander'),
           # 'cha': Animal('cha','/home/bellijjy/Chapati.tar/Chapati/Chapati'),
        #  'dav': Animal('dav','/home/bellijjy/Dave.tar/Dave/Dave'),
         #  'dud': Animal('dud','/home/bellijjy/Dudley'),
         #   'bon' : Animal('bon', '/home/bellijjy/Bond'),
    'fra' : Animal('fra', '/local2/Jan/Frank/Frank'),
    'gov' : Animal('gov', '/local2/Jan/Government/Government'),
    'egy' : Animal('egy', '/local2/Jan/Egypt/Egypt'), 
    'remy': Animal('remy', '/local2/Jan/Remy/Remy'),
    "Fiv" : Animal("Fiv", "/home/dekorvyb/Downloads/Fiv"),
    "bon" : Animal("bon", "/home/dekorvyb/Downloads/Bon")}

# In[4]:


def neuron_ids_for_specific_animal_and_subarea(area, animal, animals_dict):
    #Information about all recorded neurons such as brain area.
    df = sdd.make_neuron_dataframe_modified(animals_dict)

    #subdividing the meta-index by theme
    splitted_df = divis.split_neuron_dataframe_informationally(df, ['area', 'animal'])
    
    #subdividing to acess task/behav. state -- this is joined with the meta-index above via 'get_matching_pairs' below
    
    #HAVE TO ADD OTHER ANIMAL NAMES

    # for the sake of computing deleted all animals except for frank:
    # corriander, conley, dave, dudley, bond, chapati, remy, egypt, government, frank
    splitted_epoch_dataframe = divis.split_neuron_dataframe_informationally(task.make_epochs_dataframe(animals_dict, egypt, remy, government, frank, bon),['type'])
    
    area_animal_df = splitted_df[area, animal]
    
    sleep_area_animal_df = divis.get_matching_pairs(area_animal_df, splitted_epoch_dataframe['sleep',].index)
    wake_area_animal_df = divis.get_matching_pairs(area_animal_df, splitted_epoch_dataframe['run',].index)
    
    
    neuron_list_id_sleep = sleep_area_animal_df['neuron_id'].tolist()
    neuron_list_id_wake = wake_area_animal_df['neuron_id'].tolist()
    
    #Getting the epochs per day, relative to brain region (input) and sleep/run (input)
    sleep_epochs_per_day = behav.get_epochs_by_day(sleep_area_animal_df.index)
    wake_epochs_per_day = behav.get_epochs_by_day(wake_area_animal_df.index)

    #generating a dict, relative to brain region and sleep/run, of the neuron_ids per epoch per day
    embedded_day_epoch_dict_sleep = behav.embedded_day_epoch_dict(sleep_epochs_per_day, neuron_list_id_sleep)
    embedded_day_epoch_dict_wake = behav.embedded_day_epoch_dict(wake_epochs_per_day, neuron_list_id_wake)

    #checking for overlap of the epoch/day combinations for sleep/run and generating the final conjoinded dict of run/sleep, day, epoch, neuron_id
    conjoined_key_epochs_per_day_dict = behav.conjoined_dict_with_overlap_checked(embedded_day_epoch_dict_wake, embedded_day_epoch_dict_sleep)
    
    return conjoined_key_epochs_per_day_dict


# In[6]:


def get_spike_data(conjoined_key_epochs_per_day_dict, time_len_splitted_chunks, area, animal):
    '''
    Input: conjoined_key_epochs_per_day_dict: neuron ids relative to day, epoch and behav state
            time_len_splitted_chunks: desired length of temporal intervals for which the parameters get evaluated
    Returns: embedded dict (day/epoch/time_chunk) with the neuronal data as values and time as index
    '''
    
    
    animals = {#'con': Animal('con','/home/bellijjy/Conley.tar/Conley/con'),
               #'Cor': Animal('Cor','/home/bellijjy/Corriander.tar/Corriander/Cor'),
              #  'cha': Animal('cha','/home/bellijjy/Chapati.tar/Chapati/Chapati/cha'),
             # 'dav': Animal('dav','/home/bellijjy/Dave.tar/Dave/Dave/dav'),
             #  'dud': Animal('dud','/home/bellijjy/Dudley/dud'),
             #   'bon' : Animal('bon', '/home/bellijjy/Bond/bon'),
                  'fra' : Animal('fra', '/local2/Jan/Frank/Frank/fra'),
                  'gov' : Animal('gov', '/local2/Jan/Government/Government/gov'),
                'egy' : Animal('egy', '/local2/Jan/Egypt/Egypt/egy'), 
              'remy': Animal('remy', '/local2/Jan/Remy/Remy/remy'),
    "Fiv" : Animal("Fiv", "/home/dekorvyb/Downloads/Fiv"),
          "bon" : Animal("bon", "/home/dekorvyb/Downloads/Bon/bon")}

    
    #getting the spike data itself
    spike_dict = behav.coarse_grained_spike_generator_dict(conjoined_key_epochs_per_day_dict, animals)
    
    neuron_ids = neuron_ids_for_specific_animal_and_subarea(area, animal)
     
    #getting the time index of the neuronal data
    time_dict = sdd.time_index_dict(neuron_ids, animals)  
    
    #summing over the neurons in each epoch and associating the spike trains with time index
    spike_dict_summed = sum_sep.sum_time_series_with_time_index_from_embedded_state_day_epoch_key_values_dict(spike_dict, time_dict)
    print(spike_dict_summed)
    #subdividing time index into intervals of 5 seconds
    splitted_by_sec_spike_dict = sum_sep.time_index_seperator(spike_dict_summed, time_len_splitted_chunks)
    
    
    return splitted_by_sec_spike_dict


def get_spikes(conjoined_key_epochs_per_day_dict, area, animal):
    '''
    Function from above without time chunks.
    Input: conjoined_key_epochs_per_day_dict: neuron ids relative to day, epoch and behav state
            
    Returns: embedded dict (day/epoch/time_chunk) with the neuronal data as values and time as index
    '''
    
    #redefining the animal dict with the short_name appended at the end

    animals = {#'con': Animal('con','/home/bellijjy/Conley.tar/Conley/con'),
              # 'Cor': Animal('Cor','/home/bellijjy/Corriander.tar/Corriander/Cor'),
              #  'cha': Animal('cha','/home/bellijjy/Chapati.tar/Chapati/Chapati/cha'),
              #'dav': Animal('dav','/home/bellijjy/Dave.tar/Dave/Dave/dav'),
              # 'dud': Animal('dud','/home/bellijjy/Dudley/dud'),
              #  'bon' : Animal('bon', '/home/bellijjy/Bond/bon'),
                  'fra' : Animal('fra', '/local2/Jan/Frank/Frank'),
                  'gov' : Animal('gov', 'local2/Jan/Government/Government'),
                'egy' : Animal('egy', 'local2/Jan/Egypt/Egypt'), 
              'remy': Animal('remy', 'local2/Jan/Remy/Remy'),
    "Fiv" : Animal("Fiv", "/home/dekorvyb/Downloads/Fiv"),
          "bon" : Animal("bon", "/home/dekorvyb/Downloads/Bon")}
    
    #getting the spike data itself
    spike_dict = behav.coarse_grained_spike_generator_dict(conjoined_key_epochs_per_day_dict, animals)
    
    neuron_ids = neuron_ids_for_specific_animal_and_subarea(area, animal)
     
    #getting the time index of the neuronal data
    time_dict = sdd.time_index_dict(neuron_ids, animals)  
    
    #summing over the neurons in each epoch and associating the spike trains with time index
    spike_dict_summed = sum_sep.sum_time_series_with_time_index_from_embedded_state_day_epoch_key_values_dict(spike_dict, time_dict)
    
    return spike_dict_summed

# In[ ]:




print(animals["bon"])
print(bon)