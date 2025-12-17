#pragma once

#include "instance/instance.hpp"
#include <vector>
#include <iostream>

namespace bmcp {
/***************************************************
 * The Solution class represents a solution for the
 * Balanced Multiway Cut Problem (Biobjective).
 ***************************************************/
class Solution {
    public:

    /****************************
     * The instance been solved.
     ****************************/
     const Instance & instance;

    /****************************
     * Components Size
     ****************************/
    std::vector<unsigned> components_size;

    /*************************
     * The solution's cost -> cost[0] : custo do corte, cost[1] : balanceamento
     *************************/
    std::vector<double> cost;


    /**********************************************************
     * Returns true if costA dominates costB; false otherwise.
     *
     * @param costA the first cost been compared.
     * @param costB the second cost been compared.
     *
     * @return true if costA dominates costB; false otherwise.
     **********************************************************/
    static bool dominates(const std::vector<double> & costA,
                          const std::vector<double> & costB);
    
    /*******************************************************************
     * Verifies whether this solution dominates the specified one.
     *
     * @param solution the solution whose domination is to be verified.
     *
     * @return true if this instance dominated the specified one;
     *         false otherwise.
     *******************************************************************/
    bool dominates(const Solution & solution) const;

    private:
    /******************************
     * Initializes a new solution.
     ******************************/
    void init();

    public:
    /**********************************************
     * Constructs a new solution
     **********************************************/
    Solution(const Instance & instance);


    /********************************
     * Constructs an empty solution.
     ********************************/
    Solution();

    // Constrói uma solução preenchida -> usado pelo Decoder e Solver
    Solution(const Instance & instance, 
             const std::vector<unsigned> & components_size, 
             const std::vector<double> & cost);

    /*******************************************************
     * Standard input operator.
     *
     * @param is       standard input stream object.
     * @param solution the solution.
     *
     * @return the stream object.
     *******************************************************/
    friend std::istream & operator >>(std::istream & is,
                                      Solution & solution);

    /*************************************************************
     * Standard output operator.
     *
     * @param os       standard output stream object.
     * @param solution the solution.
     *
     * @return the stream object.
     *************************************************************/
    friend std::ostream & operator <<(std::ostream & os,
                                      const Solution & solution);
};

}
