# Next steps

MAIN REMARK:
   1. Move as much functionality as possile out of the interface methods and put them in the logic objects.
   2. Make as many widgets reliant upon multiple inheritance as possible.

1. Priorities:
   1. Finalize dataset selection and creation
      1. Create individual sample manipulation menu
      2. Datasets should be selected in a table instead - better interface, can put more info, etc
         1. Need audio dataset config/descriptor file - modify load_existing to make changes based on that.
            1. >audio params
               1. .......
            2. >stats
               1. n_labels
               2. total_samples

            3. MEANS that i need to keep track of these values in the object itself.
            4. Once some change is made - record the descriptor (good condition?) on label selection or something.


         2. Make a method that will update/create the descriptor
         3. RENAME functionality
         4. General layout -> New, rename, delete.
         5. Number of labels, total number of samples. 
         6. Recording length, and other audio parameters that get locked once one of the recordings is made?
         7. Get rid of the outputs section, move it where the label selection is supposed to be
         8. Custom tables that would have both a directory model and a display table, which would refer to any updates inside the directory.
         9. Or have a descriptor file for each of the recorded datasets that get updated as soon as any modifications are made.
         10. When IMGDATASET tab is active, model training widget activates
      3. SWITCH the outputs with the model section - makes more sense both for usage and in based on how the thing is supposed to be used in terms of action sequence.
      4. The outputs are saved as part of the dataset as well, all image datasets that are created from it inherit all the label parameters. 
      5. CREATE IMAGE DATASET BUTTON: 
         1. Dialog for label selection (all by default)
         2. A information section that says that current spec parameters are going to be used for this new dataset.
   
   2. Model training inside the gui
      1. Selection - table with some basic parameters (probably in a tab)
         1. Accuracy, nlayers, type, dataset, spec size, train time
         2. Load model button - initializes from all the config files
         3. Model also saves the output mappings
            1. Make mappings closer to the model selection so that it is more intuitive.
      2. Reloading
   3. Create good datastructures for the output mappings
      1. Most likely a base class that calls the functions with kwargs that were passed during init.
      2. Would be pretty simple in general
      3. Probability of triggering
   4. Visuals: 
      1. Enable/disable spectrogram colormap


2. Models: 
   1. UI
      1. Menu for conv net config
      2. Graph of train/test scores per epoch, using the Audio wave display
      3. Progress bar
   2. Saving/loading!
   3. Config restoration, locking
   4. Separate config in the dir that specifies:
      1. The image dataset used
      2. Conv net settings
3. Audio dataset:
   1. Create image dataset using the current spectrogram parameters
   2. Write new config as well
4. Image datasets
   1. Config file in the directory for loading appropriate spectrogram settings
   2. Lock the spectrogram config once an existing dataset is selected
5. Outputs
   1. Map to midi devices
6. Settings
   1. Midi device selection
   2. Anything else in the config file should be accessible here
7. Parameter tuning
   1. Find other things that might be relevant but are not there yet
8. Menu:
   1. Save/load functionality
9.  Image datasets
   2. Loading saving
10. Implementation
   3. Check if the base code needs refactoring
   4. Try to use subclasses as much as possible
11. Console 
   5. Classification details
   6. Training process/etc

   
# Bugs

1. Audio playback
2. Classifier output


## Main task till 16/12

1. End-to-end:
   1. Create dataset
   2. Create two new labels
   3. Record ~5 samples each
   4. Assign two different shell outputs 
   5. Train a model inside the GUI, can be without config for now
   6. Fix the classification pipeline
      1. Add the methods for accessing the new classifier
      2. Organize outputs in a way that makes sense
   7. Add visual indicators for triggers
   8. Playback doesn't matter for now
